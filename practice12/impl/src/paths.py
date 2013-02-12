"""
This module handles paths stack in context of the system.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""



import os


class NonAbsolutePathError(RuntimeError):
    pass

class NoSuchNestedPathError(RuntimeError):
    pass


def push_path(context, path):
    """
    Push path to stack in context.

    Path must be absolute.
    """
    if os.path.isabs(path):
        context.paths_stack.append(path)
    else:
        raise NonAbsolutePathError


def pop_path(context):
    """
    Pop path from stack in context.

    Path is absolute.
    """
    return context.paths_stack.pop()


def get_path(context):
    """
    Return the path on top of stack in context.
    """
    return context.paths_stack[-1]


def ensure_path(context):
    """
    Get the correct current path from stack in context and 
    change current directory to there.
    """
    os.chdir(get_path(context))


def nest_path_absolute(context, path):
    """
    Receive path, push the real path of it to stack in context and 
    change current directory to there.
    """
    try:
        os.chdir(path)
    except:
        raise NoSuchNestedPathError

    push_path(context, path)
    ensure_path(context)


def nest_path_from_root(context, path):
    """
    Receive path, relative to the root of framework, 
    push it to stack in context and change current directory to there.
    """
    new_path = os.path.join(context.settings.framework_root_dir, path)
    nest_path_absolute(context, new_path)


def nest_path_from_benchmark_root(context, path):
    """
    Receive path, relative to the root of benchmark directory, 
    push it to stack in context and change current directory to there.
    """
    new_path = os.path.join(context.settings.benchmark_root_dir, path)
    nest_path_absolute(context, new_path)


def nest_path(context, path):
    """
    Receive relative path, push the real path of it to stack in context and 
    change current directory to there.
    """
    new_path = os.path.join(get_path(context), path)
    nest_path_absolute(context, new_path)


def unnest_path(context):
    """
    Pop the path from stack in context and
    change current directory to current top path of stack.
    """
    pop_path(context)
    try:
        ensure_path(context)
    except:
        # Fails when stack is empty after popping
        pass
