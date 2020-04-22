#
# dsargparse.py
#
# Copyright (c) 2016 Junpei Kawamoto
#
# This software is released under the MIT License.
#
# http://opensource.org/licenses/mit-license.php
#
"""dsargparse: docstring based argparse.

dsargparse is a wrapper of argparse library which prepares helps and descriptions
from docstrings. It also sets up functions to be run for each sub command,
and provides a helper function which parses args and run a selected command.
"""
import argparse
import itertools
import inspect
import textwrap
import re

# Load objects defined in argparse.
for name in argparse.__all__:
    if name != "ArgumentParser":
        globals()[name] = getattr(argparse, name)
__all__ = argparse.__all__


_HELP = "help"
_DESCRIPTION = "description"
_FORMAT_CLASS = "formatter_class"

_KEYWORDS_ARGS = ("Args:",)
_KEYWORDS_OTHERS = ("Returns:", "Raises:", "Yields:", "Usage:")
_KEYWORDS = _KEYWORDS_ARGS + _KEYWORDS_OTHERS


def _checker(keywords):
    """Generate a checker which tests a given value not starts with keywords."""
    def _(v):
        """Check a given value matches to keywords."""
        for k in keywords:
            if k in v:
                return False
        return True
    return _


def _parse_args(args_desc):
    '''Parse an Args description

    Parse given args description and return in dictionary form.

    Args:
        args_desc: description of args.

    Returns:
        a dictionary.
    '''
    def extract_key(line):
        '''exctract a key from a line'''
        key = re.sub(r'(^[^\s]+?):(.|\n)*$', r'\1', line)
        return key

    def extract_value(line):
        '''exctract a key from a line'''
        value = re.sub(r'^[^\s]+?:((.|\n)*)$', r'\1', line).strip()
        return value

    argmap = {}

    args = list(filter(bool, args_desc.splitlines()))
    for idx, arg_line in enumerate(args):
        if _starts_with_white(arg_line): continue
        assert ':' in arg_line
        additional_lines = itertools.takewhile(_starts_with_white, args[idx + 1:])
        if additional_lines: arg_line += '\n' + '\n'.join(additional_lines)
        key, value = extract_key(arg_line), extract_value(arg_line)
        argmap[key] = value
    return argmap


def _starts_with_white(line):
    '''check if starts with a white

    Args:
        line: a string line

    Returns:
        bool
    '''
    return bool(re.match(r'^\s+.*$', line))


def _parse_doc(doc):
    """Parse a docstring.

    Parse a docstring and extract three components; headline, description,
    and map of arguments to help texts.

    Args:
      doc: docstring.

    Returns:
      a dictionary.
    """
    lines = doc.strip().splitlines()
    descriptions = list(filter(bool, itertools.takewhile(_checker(_KEYWORDS), lines)))

    if len(descriptions) > 0: description = descriptions[0]
    if len(descriptions) > 1: description += "\n\n" + textwrap.dedent("\n".join(descriptions[1:]))

    args = list(filter(bool, itertools.takewhile(
        _checker(_KEYWORDS_OTHERS),
        itertools.dropwhile(_checker(_KEYWORDS_ARGS), lines))))

    argmap = _parse_args(textwrap.dedent('\n'.join(args[1:])))
    return dict(headline=descriptions[0], description=description, args=argmap)


class _SubparsersWrapper(object):
    """Wrapper of the action object made by argparse.ArgumentParser.add_subparsers.

    To create an instance, the constructor takes a reference to an instance of
    the action class.
    """
    __slots__ = ("__delegate")

    def __init__(self, delegate):
        self.__delegate = delegate

    def add_parser(self, func=None, name=None, **kwargs):
        """Add parser.

        This method makes a new sub command parser. It takes same arguments
        as add_parser() of the action class made by
        argparse.ArgumentParser.add_subparsers.

        In addition to, it takes one positional argument `func`, which is the
        function implements process of this sub command. The `func` will be used
        to determine the name, help, and description of this sub command. The
        function `func` will also be set as a default value of `cmd` attribute.

        If you want to choose name of this sub command, use keyword argument
        `name`.

        Args:
          func: function implements the process of this command.
          name: name of this command. If not give, the function name is used.

        Returns:
          new ArgumentParser object.

        Raises:
          ValueError: if the given function does not have docstrings.
        """
        if func:
            if not func.__doc__:
                raise ValueError(
                    "No docstrings given in {0}".format(func.__name__))

            info = _parse_doc(func.__doc__)
            if _HELP not in kwargs or not kwargs[_HELP]:
                kwargs[_HELP] = info["headline"]
            if _DESCRIPTION not in kwargs or not kwargs[_DESCRIPTION]:
                kwargs[_DESCRIPTION] = info["description"]
            if _FORMAT_CLASS not in kwargs or not kwargs[_FORMAT_CLASS]:
                kwargs[_FORMAT_CLASS] = argparse.RawTextHelpFormatter

            if not name:
                name = func.__name__ if hasattr(func, "__name__") else func

            res = self.__delegate.add_parser(name, argmap=info["args"], **kwargs)
            res.set_defaults(cmd=func)

        else:
            res = self.__delegate.add_parser(name, **kwargs)

        return res

    def __repr__(self):
        return self.__delegate.__repr__()


class ArgumentParser(argparse.ArgumentParser):
    """Customized ArgumentParser.

    This customized ArgumentParser will add help and description automatically
    based on docstrings of main module and functions implements processes of
    each command. It also provides :meth:`parse_and_run` method which helps parsing
    arguments and executing functions.

    This class takes same arguments as argparse.ArgumentParser to construct
    a new instance. Additionally, it has a positional argument ``main``,
    which takes the main function of the script ``dsargparse`` library called.
    From the main function, it extracts doctstings to set command descriptions.
    """

    def __init__(self, main=None, argmap=None, *args, **kwargs):
        if main:
            if _DESCRIPTION not in kwargs or not kwargs[_DESCRIPTION]:
                info = _parse_doc(inspect.getmodule(main).__doc__)
                kwargs[_DESCRIPTION] = info[_DESCRIPTION]
            if _FORMAT_CLASS not in kwargs or not kwargs[_FORMAT_CLASS]:
                kwargs[_FORMAT_CLASS] = argparse.RawTextHelpFormatter
        self.__argmap = argmap if argmap else {}

        super(ArgumentParser, self).__init__(*args, **kwargs)

    def add_subparsers(self, **kwargs):
        """Add subparsers.

        Keyword Args:
          same keywords arguments as ``argparse.ArgumentParser.add_subparsers``.

        Returns:
          an instance of action class which is used to add sub parsers.
        """
        return _SubparsersWrapper(
            super(ArgumentParser, self).add_subparsers(**kwargs))

    def add_argument(self, *args, **kwargs):
        """Add an argument.

        This method adds a new argument to the current parser. The function is
        same as ``argparse.ArgumentParser.add_argument``. However, this method
        tries to determine help messages for the adding argument from some
        docstrings.

        If the new arguments belong to some sub commands, the docstring
        of a function implements behavior of the sub command has ``Args:`` section,
        and defines same name variable, this function sets such
        definition to the help message.

        Positional Args:
          same positional arguments as argparse.ArgumentParser.add_argument.

        Keyword Args:
          same keywards arguments as argparse.ArgumentParser.add_argument.
        """
        if _HELP not in kwargs:
            for name in args:
                name = name.replace("-", "")
                if name in self.__argmap:
                    kwargs[_HELP] = self.__argmap[name]
                    break
        return super(ArgumentParser, self).add_argument(*args, **kwargs)

    def parse_and_run(self, **kwargs):
        """Parse arguments and run the selected command.

        Keyword Args:
          same keywords arguments as ``argparse.ArgumentParser.parse_args``.

        Returns:
          any value the selected command returns. It could be ``None``.
        """
        return self._dispatch(**vars(self.parse_args(**kwargs)))

    @staticmethod
    def _dispatch(cmd, **kwargs):
        """Dispatch parsed arguments to a command to be run.
        """
        return cmd(**kwargs)
