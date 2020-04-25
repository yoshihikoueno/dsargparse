#! /usr/bin/env python
# pylint: disable=protected-access
#
# dsargparse_test.py
#
# Copyright (c) 2016 Junpei Kawamoto
#
# This software is released under the MIT License.
#
# http://opensource.org/licenses/mit-license.php
#
""" Unit tests for dsargparse module.
"""
import argparse
import textwrap
import unittest

import dsargparse


class TestParser(unittest.TestCase):
    """Unit tests for _parse_doc function.
    """
    def test_minimum_document(self):
        """Test for a minimum docstring.
        """
        ans = dsargparse._parse_doc(dsargparse._checker)
        self.assertEqual(
            ans["headline"],
            "Generate a checker which tests a given value not starts with keywords.")
        self.assertEqual(
            ans["description"],
            "Generate a checker which tests a given value not starts with keywords.")
        self.assertEqual(len(ans["args"]), 0)

    def test_type(self):
        """ Test for a docstring which doesn't have descriptions.
        """
        def test():
            """Test docstring.

            Args:
              one ( int ) : definition of one.
              two ( float ) : definition of two.

            Returns:
              some value.
            """
            return

        ans = dsargparse._parse_doc(test)
        self.assertEqual(ans["headline"], "Test docstring.")
        self.assertEqual(
            ans["description"],
            textwrap.dedent("""\
            Test docstring."""))
        self.assertIn('one', ans['args'])
        self.assertEqual(ans['args']['one']['type'], int)
        self.assertIn('two', ans["args"])
        self.assertEqual(ans['args']['two']['type'], float)

    def test_collective_type(self):
        """ Test for a docstring which doesn't have descriptions.
        """
        def test():
            """Test docstring.

            Args:
              one ( list[int] ) : definition of one.
              two ( tuple[ float ] ) : definition of two.

            Returns:
              some value.
            """
            return

        ans = dsargparse._parse_doc(test)
        self.assertEqual(ans["headline"], "Test docstring.")
        self.assertEqual(
            ans["description"],
            textwrap.dedent("""\
            Test docstring."""))
        self.assertIn('one', ans['args'])
        self.assertEqual(ans['args']['one']['type'], int)
        self.assertEqual(ans['args']['one']['nargs'], '+')
        self.assertIn('two', ans["args"])
        self.assertEqual(ans['args']['two']['type'], float)
        self.assertEqual(ans['args']['two']['nargs'], '+')

    def test_default_inference(self):
        """ Test for a docstring which doesn't have descriptions.
        """
        def test(one=324, two=0.234):
            """Test docstring.

            Args:
              one ( int ) : definition of one.
              two ( float ) : definition of two.

            Returns:
              some value.
            """
            return

        ans = dsargparse._parse_doc(test)
        self.assertEqual(ans["headline"], "Test docstring.")
        self.assertEqual(
            ans["description"],
            textwrap.dedent("""\
            Test docstring."""))
        self.assertIn('one', ans['args'])
        self.assertEqual(ans['args']['one']['type'], int)
        self.assertEqual(ans['args']['one']['default'], 324)
        self.assertIn('two', ans["args"])
        self.assertEqual(ans['args']['two']['type'], float)
        self.assertEqual(ans['args']['two']['default'], 0.234)

    def test_default_inference_without_docstring_for_type(self):
        """ Test for a docstring which doesn't have descriptions.
        """
        def test(one=324, two=0.234):
            """Test docstring.

            Args:
              one: definition of one.
              two: definition of two.

            Returns:
              some value.
            """
            return

        ans = dsargparse._parse_doc(test)
        self.assertEqual(ans["headline"], "Test docstring.")
        self.assertEqual(
            ans["description"],
            textwrap.dedent("""\
            Test docstring."""))
        self.assertIn('one', ans['args'])
        self.assertEqual(ans['args']['one']['type'], int)
        self.assertEqual(ans['args']['one']['default'], 324)
        self.assertIn('two', ans["args"])
        self.assertEqual(ans['args']['two']['type'], float)
        self.assertEqual(ans['args']['two']['default'], 0.234)

    def test_docstring_without_description(self):
        """ Test for a docstring which doesn't have descriptions.
        """
        def test():
            """Test docstring.

            Args:
              one: definition of one.
              two: definition of two.

            Returns:
              some value.
            """
            return

        ans = dsargparse._parse_doc(test)
        self.assertEqual(ans["headline"], "Test docstring.")
        self.assertEqual(
            ans["description"],
            textwrap.dedent("""\
            Test docstring."""))
        self.assertIn("one", ans["args"])
        self.assertEqual(ans["args"]["one"]['help'], "definition of one.")
        self.assertIn("two", ans["args"])
        self.assertEqual(ans["args"]["two"]['help'], "definition of two.")

    def test_docstring_with_multiline_args(self):
        """ Test for a docstring which doesn't have descriptions.
        """
        def test():
            """Test docstring.

            Args:
              one: definition of one.
                More detail description about one.
                More detail description about one.
                More detail description about one.
              two: definition of two.
                More detail description about two.
                More detail description about two.
                More detail description about two.

            Returns:
              some value.
            """
            return

        ans = dsargparse._parse_doc(test)
        self.assertEqual(ans["headline"], "Test docstring.")
        self.assertEqual(
            ans["description"],
            textwrap.dedent("""\
            Test docstring."""))
        self.assertIn("one", ans["args"])
        self.assertEqual(
            ans["args"]["one"]['help'],
            textwrap.dedent('''\
                definition of one.
                  More detail description about one.
                  More detail description about one.
                  More detail description about one.''')
        )
        self.assertIn("two", ans["args"])
        self.assertEqual(
            ans["args"]["two"]['help'],
            textwrap.dedent('''\
                definition of two.
                  More detail description about two.
                  More detail description about two.
                  More detail description about two.''')
        )

    def test_docstring_without_args(self):
        """ Test for a docstring which doesn't have args.
        """
        def test():
            """Test docstring.

            This function do something.

            Returns:
              some value.
            """
            return
        ans = dsargparse._parse_doc(test)
        self.assertEqual(ans["headline"], "Test docstring.")
        self.assertEqual(
            ans["description"],
            textwrap.dedent("""\
            Test docstring.

            This function do something."""))
        self.assertEqual(len(ans["args"]), 0)


class TestModule(unittest.TestCase):

    def test_modules(self):
        """ Test dsargparse module has same objects as argparse.
        """
        for name in argparse.__all__:
            self.assertTrue(hasattr(dsargparse, name))

    def test_filetype(self):
        """ Test create dsargparse's filetype.
        """
        self.assertIsNotNone(dsargparse.FileType("r"))





if __name__ == "__main__":
    unittest.main()
