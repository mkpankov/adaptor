"""
This module handles paths stack in self of the system.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""


import os

import ipdb



class NonAbsolutePathError(RuntimeError):
    pass



class NoSuchNestedPathError(RuntimeError):
    pass



class PathsManager():
    """Management of paths: current directory, nesting."""
    def __init__(self,
                 framework_root_dir,
                 benchmark_root_dir,
                 benchmark_bin_dir):
        self.framework_root_dir = framework_root_dir
        self.benchmark_root_dir = benchmark_root_dir
        self.benchmark_bin_dir = benchmark_bin_dir
        self.paths_stack = []


    def push_path(self, path):
        """
        Push path to stack in self.

        Path must be absolute.
        """
        if os.path.isabs(path):
            self.paths_stack.append(path)
        else:
            raise NonAbsolutePathError


    def pop_path(self):
        """
        Pop path from stack in self.

        Path is absolute.
        """
        path = self.paths_stack.pop()
        return path


    def get_path(self):
        """
        Return the path on top of stack in self.
        """
        return self.paths_stack[-1]


    def ensure_path(self, path=None):
        """
        Get the correct current path from stack in self and
        change current directory to there.
        """
        if path is None:
            os.chdir(self.get_path())
        else:
            os.chdir(path)


    def nest_path_absolute(self, path):
        """
        Receive path, push the real path of it to stack in self and
        change current directory to there.
        """
        try:
            os.chdir(path)
        except OSError:
            raise NoSuchNestedPathError

        self.push_path(path)
        self.ensure_path()


    def nest_path_from_root(self, path):
        """
        Receive path, relative to the root of framework,
        push it to stack in self and change current directory to there.
        """
        new_path = os.path.join(self.framework_root_dir, path)
        self.nest_path_absolute(new_path)


    def nest_path_from_benchmark_root(self, path):
        """
        Receive path, relative to the root of benchmark directory,
        push it to stack in self and change current directory to there.
        """
        new_path = os.path.join(self.benchmark_root_dir, path)
        self.nest_path_absolute(new_path)


    def nest_path(self, path):
        """
        Receive relative path, push the real path of it to stack in self and
        change current directory to there.
        """
        new_path = os.path.join(self.get_path(), path)
        self.nest_path_absolute(new_path)


    def unnest_path(self):
        """
        Pop the path from stack in self and
        change current directory to current top path of stack.
        """
        top_path = self.pop_path()
        self.ensure_path(top_path)
