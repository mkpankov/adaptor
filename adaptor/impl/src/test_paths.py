#!/usr/bin/env python

"""
Test the paths management module.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

import unittest
import paths
import collections
import textwrap
import os



class TestPathsManagement(unittest.TestCase):
    def setUp(self):
        self.paths_manager = paths.PathsManager('..',
                                                '../data',
                                                '../data/bin')
        self.base_path = os.getcwd()


    def test_push(self):
        self.assertEquals(self.paths_manager.paths_stack, [])
        self.paths_manager.push_path(os.path.devnull)
        self.assertEquals(self.paths_manager.paths_stack,
                          [os.path.devnull])


    def test_push_exception(self):
        self.assertRaises(paths.NonAbsolutePathError,
                          self.paths_manager.push_path,
                          '..')




if __name__ == '__main__':
    unittest.main()
