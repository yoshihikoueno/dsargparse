dargparse
==========
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

dargparse is a wrapper of argparse library which prepares helps and descriptions
from docstrings. It also sets up functions to be run for each sub command,
and provides a helper function which parses args and run a selected command.

Using this library, you don't need to write same texts in docstrings, help,
and description.

Example
---------
Suppose to make a following trivial greeting command consists of two subcommands
supplied as functions shown below.

```python
"""Sample command of dargparse package.

This text will be used as description of this command.
"""
def greeting(title, name): # pylint: disable=unused-argument
    """Print a greeting message.

    This command print "Good morning, <title> <name>.".

    Args:
      title: title of the person.
      name: name of the person.
    """
    print("Good morning, {title} {name}.".format(**locals()))
    return 0


def goodbye(name): # pylint: disable=unused-argument
    """Print a goodbye message.

    This command print "Goodbye, <name>.".

    Args:
      name: name of the person say goodbye to.
    """
    print("Goodbye, {name}".format(**locals()))
    return 0
```

The `dargparse` reduces codes you need from the **before**
```python
# Before dargparse
import sys
import textwrap

import argparse

def main():
    """ The main function.
    """
    parser = argparse.ArgumentParser(
      description=textwrap.dedent("""\
        Sample command of dargparse package.

        This text will be used as description of this command.
        """))
    subparsers = parser.add_subparsers()

    greeting_cmd = subparsers.add_parser(
        "greeting",
        help="Print a greeting message.",
        description=textwrap.dedent("""\
            Print a greeting message.

            This command print "Good morning, <title> <name>".
            """))
    greeting_cmd.add_argument(
        "title", help="title of the person say greetings to")
    greeting_cmd.add_argument(
        "name", help="name of the person say greetings to.")
    greeting_cmd.set_defaults(cmd=greeting)

    goodbye_cmd = subparsers.add_parser(
        "goodbye",
        help="Print a goodbye message.",
        description=textwrap.dedent("""\
            Print a goodbye message.

            This command print "Goodbye, <name>".
            """))
    goodbye_cmd.add_argument(
        "name", help="name of the person say goodbye to.")
    goodbye_cmd.set_defaults(cmd=goodbye)

    args = parser.parse_args()
    return args.cmd(**args)


if __name__ == "__main__":
    sys.exit(main())
```
to the **after**
```python
# After dargparse
import sys

import dargparse

def main():
    """ The main function.
    """
    parser = dargparse.ArgumentParser(main=main)
    subparsers = parser.add_subparsers()

    greeting_cmd = subparsers.add_parser(greeting)
    greeting_cmd.add_argument("title")
    greeting_cmd.add_argument("name")

    goodbye_cmd = subparsers.add_parser(goodbye)
    goodbye_cmd.add_argument("name")

    return parser.parse_and_run()


if __name__ == "__main__":
    sys.exit(main())
```


Usage
------
`dargparse` is a simple wrapper of the original `argparse`. To use it, install
this package and just adding `d` to your import command i.e. from
`import argparse` to `import dargparse`. In addition to all API `argparse` has,
`dargparse` updates three functions; constructor of `ArgumentParser` object,
`ArgumentParser.add_argument`, and `add_parser` method of the action class made
by `ArgumentParser.add_subparsers()`, and give one new method
`ArgumentParser.parse_and_run`.

### `dargparse.ArgumentParser`
In addition to the keyword arguments `argparse.ArgumentParser` takes,
this constructor has keyword argument `main` which takes the main function.

If you give the main function, you don't need to set `description`, and
`formatter_class` also will be set automatically.

### `add_argument`
This method adds a new argument to the current parser. The function is
same as `argparse.ArgumentParser.add_argument`. But, this method
tries to determine help messages for the adding argument from some
docstrings.

If the new arguments belong to some subcommand, the docstring
of a function implements behavior of the subcommand has `Args:` section,
and defines same name variable, this function sets such
definition to the help message.

### `add_parser`
After constructing subparsers by `subparsers = parser.add_subparsers()`,
you may call `subparsers.add_parser` to add a new subcommand.

The add_parser has a new positional argument `func` which takes a function
to be called in order to run the subcommand. The `func` will be used
to determine the name, help, and description of this subcommand. The
function `func` will also be set as a default value of `cmd` attribute.

The add_parser also has as same keyword arguments as `add_parser` of `argparse`
library.

### `ArgumentParser.parse_and_run`
This method parses arguments and run the selected command. It returns a value
which the selected command returns. This function takes as same arguments as
`ArgumentParser.parse_args`.


### Other functions and arguments
See more detail of original `argparse`.
- https://docs.python.org/3/library/argparse.html
- https://docs.python.org/2.7/library/argparse.html


License
=========
This software is released under the MIT License, see [LICENSE](LICENSE).
