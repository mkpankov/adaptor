"""
This module handles paths stack in self of the system.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""


import os



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
        self.previous_dir = os.getcwd()

        # Pay attention to the ordering:
        # in case we don't define previous_dir before possible
        # exception raise, __del__ is going to complain that
        # previous_dir is not defined.
        # __del__ is called even though the __init__ raises an exception.
        paths = [framework_root_dir,
                 benchmark_root_dir,
                 benchmark_bin_dir]

        for path in paths:
            if not os.path.isabs(path):
                raise NonAbsolutePathError

        self.framework_root_dir = os.path.abspath(framework_root_dir)
        self.benchmark_root_dir = os.path.abspath(benchmark_root_dir)
        self.benchmark_bin_dir = os.path.abspath(benchmark_bin_dir)
        self.paths_stack = []


    def __del__(self):
        os.chdir(self.previous_dir)


    def push_path(self, path):
        """
        Push path to stack in self.

        Path must be absolute.
        """
        if os.path.isabs(path):
            abspath = os.path.abspath(path)
            self.paths_stack.append(abspath)
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
        try:
            path = self.paths_stack[-1]
        except IndexError:
            path = self.framework_root_dir

        return path


    def ensure_path(self):
        """
        Get the correct current path from stack in self and
        change current directory to there.
        """
        os.chdir(self.get_path())


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
        change current directory to there.
        """
        self.pop_path()
        self.ensure_path()
