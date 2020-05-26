dsargparse
==========
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
![dsargparse](https://jkawamoto.github.io/dsargparse/_static/dsargparse.png)

**dsargparse** aims to eliminate redundant codes for building commandline interfaces.

**dsargparse** is a wrapper of argparse library which tries to retrieve
following information from the docstring of the specified function:

- function description
- function detailed description
- arguments (options) that the function has
- help message of arguments
- type of arguments
- default value of arguments

Currently **dsargparse** supports only docstrings which align with google docstring style,
but we'd welcome contributions to make this module support more various styles.

Install
---------
Use `pip` to install.
```
$ pip install -U git+https://github.com/yoshihikoueno/dsargparse.git@master
```

Example
---------
Suppose we are to expose 2 functions `greeting` and `goodbye` to the commandline interface.

```python
def greeting(title, name):
    """Print a greeting message.

    This command print "Good morning, <title> <name>.".

    Args:
      title: title of the person.
      name: name of the person.
    """
    print("Good morning, {title} {name}.".format(**locals()))
    return


def goodbye(name): # pylint: disable=unused-argument
    """Print a goodbye message.

    This command print "Goodbye, <name>.".

    Args:
      name (str): name of the person say goodbye to.
    """
    print("Goodbye, {name}".format(**locals()))
    return
```

With built-in module `argparse`, you would need to code like below:
```python3
import argparse

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    greeting_cmd = subparsers.add_parser(
        'greeting',
        help='Print a greeting message.',
        description='Print a greeting message.\nThis command print "Good morning, <title> <name>".',
    )
    greeting_cmd.add_argument('title', help='title of the person say greetings to')
    greeting_cmd.add_argument('name', help='name of the person say greetings to.')
    greeting_cmd.set_defaults(cmd=greeting)

    goodbye_cmd = subparsers.add_parser(
        'goodbye',
        help='Print a goodbye message.',
        description='Print a goodbye message.\nThis command print "Goodbye, <name>".',
    )
    goodbye_cmd.add_argument('name', help='name of the person say goodbye to.')
    goodbye_cmd.set_defaults(cmd=goodbye)

    args = parser.parse_args()
    return args.cmd(**args)


if __name__ == "__main__":
    main()
```
Notice that there are many redundant texts in the code above.

Namely, descriptions for the functions and its options are duplicated as they are
supposed to be the same as in the function's docstring.

We can remove those redundancies by retrieving necessary information from docstring,
and this is where `dsargparse` comes in.

With `dsargparse`, you can do the same thing with much simpler code as shown below:

```python3
import dsargparse

def main():
    parser = dsargparse.ArgumentParser(main=main)
    subparsers = parser.add_subparsers()

    greeting_cmd = subparsers.add_parser(greeting, add_arguments_auto=True)
    goodbye_cmd = subparsers.add_parser(goodbye, add_arguments_auto=True)

    return parser.parse_and_run()


if __name__ == "__main__":
    main()
```

Of course you can override whatever you want simply by specifying the stuff you want to override.
```python
import dsargparse

def main():
    parser = dsargparse.ArgumentParser(main=main)
    subparsers = parser.add_subparsers()

    greeting_cmd = subparsers.add_parser(greeting)
    greeting_cmd.add_argument("title", help='some custom help here')
    greeting_cmd.add_argument("name")

    goodbye_cmd = subparsers.add_parser(goodbye)
    goodbye_cmd.add_argument("name")

    return parser.parse_and_run()


if __name__ == "__main__":
    sys.exit(main())
```
In this case, `title` option of `greeting` command will get the custom description specified by user argument,
but `dsargparse` will still try to find the description and type for other options and commands.

User specified arguments are always prioritised over what `dsargparse` finds in `dsargparse`.
We tried to keep the behavior of `dsargparse` as close as `argparse`, so all the arguments available
in `argparse` are also available in `dsargparse`.

Usage
------
You can start using `dsargparse` just like `argparse` as it inherits all the classes and functions
with the same arguments. `dsargparse` will just fill in empty arguments for you where possible.

### `dsargparse.ArgumentParser`
In addition to the keyword arguments `argparse.ArgumentParser` takes,
this constructor has keyword argument `main` which takes the main function.

If you give the main function, you don't need to set `description`, and
`formatter_class` also will be set automatically.

### `add_argument`
This method adds a new argument to the current parser. The function is
same as `argparse.ArgumentParser.add_argument`. But, this method
tries to retrieve information from the docstring.

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


License
=========
This software is released under the MIT License, see [LICENSE](LICENSE).
