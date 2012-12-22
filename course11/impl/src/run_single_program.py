#!/usr/bin/env python

"""Run experiment with specified program with given compilers."""

import sys
import os
import subprocess as sp
import textwrap as tw
import datetime as dt
import couchdbkit as ck
from couchdbkit.designer import push
import recordtype as rt
import collections as cl
import timeit
import numpy as np


class Experiment(ck.Document):
    command_build = ck.StringProperty()
    command_run = ck.StringProperty()
    stdout = ck.StringProperty()
    stderr = ck.StringProperty()
    datetime = ck.DateTimeProperty()


class PrintableStructure():
    def __str__(self):
        c = self.__class__
        print c
        s = tw.dedent("""
        {name}:
        """).format(name=c.__name__)
        for k, v in self._asdict().items():
            s += '\t{field:20}:\t{value}\n'.format(field=k, value=v)

        return s


Input = cl.namedtuple('Input',
    'benchmark_source_dir compiler base_opt')


CalibrationResultBase = cl.namedtuple('CalibrationResult',
    'total_time time dispersion variance runs_number times_list')

class CalibrationResult(PrintableStructure, CalibrationResultBase):
    pass


ValidationResultBase = cl.namedtuple('ValidationResult',
    'real_time measured_time error relative_error')

class ValidationResult(PrintableStructure, ValidationResultBase):
    pass


Settings = rt.recordtype('Settings', 
    'program_name benchmark_root_dir framework_root_dir')

BuildSettings = rt.recordtype('BuildSettings',
    'compiler base_opt optimization_flags other_flags '
    'benchmark_source_dir')

RunSettings = rt.recordtype('RunSettings',
    'benchmark_bin_dir '
    'handler_stdout handler_stderr')


class NonAbsolutePathError(RuntimeError):
    pass

class NoSuchNestedPathError(RuntimeError):
    pass


definition = \
"""
from subprocess import Popen, PIPE
def run():
    p = Popen("{command}".split(), 
              stdout=PIPE, 
              stderr=PIPE)
    return p.communicate()
"""


def main():
    """Invoke all necessary builds and experiments."""
    settings = Settings(program_name='atax', 
        framework_root_dir=os.path.join(os.path.dirname(__file__), '..')
        benchmark_root_dir=None,
        benchmark_bin_dir=None)
    settings.benchmark_root_dir = os.path.realpath(os.path.join(
        settings.framework_root_dir, '/data/sources/polybench-c-3.2/'))
    settings.benchmark_bin_dir = os.path.realpath(os.path.join(
        settings.framework_root_dir, '/data/bin/'))
    settings.paths_stack = []
    nest_path_absolute(settings, settings.framework_root_dir)

    server, db = setup_database(settings)

    perform_experiment()

    unnest_path(settings)
    assert len(settings.paths_stack) == 0


def push_path(settings, path):
    """
    Push path to stack in settings.

    Path must be absolute.
    """
    if os.path.isabs(path):
        settings.paths_stack.append(path)
    else:
        raise NonAbsolutePathError


def pop_path(settings):
    """
    Pop path from stack in settings.

    Path is absolute.
    """
    return settings.paths_stack.pop()


def get_path(settings):
    """
    Return the path on top of stack in settings.
    """
    return settings.paths_stack[-1]


def ensure_path(settings):
    """
    Get the correct current path from stack in settings and 
    change current directory to there.
    """
    os.path.chdir(get_path(settings))


def nest_path_absolute(settings, path):
    """
    Receive path, push the real path of it to stack in settings and 
    change current directory to there.
    """
    try:
        os.chdir(path)
    except:
        raise NoSuchNestedPathError

    push_path(settings, path)
    ensure_path(settings)


def nest_path_from_root(settings, path):
    """
    Receive path, relative to the root of framework, 
    push it to stack in settings and change current directory to there.
    """
    new_path = os.path.join(settings.framework_root_dir, path)
    nest_path_absolute(settings, new_path)


def nest_path_from_benchmark_root(settings, path):
    """
    Receive path, relative to the root of benchmark directory, 
    push it to stack in settings and change current directory to there.
    """
    new_path = os.path.join(settings.benchmark_root_dir, path)
    nest_path_absolute(settings, new_path)


def nest_path(settings, path):
    """
    Receive relative path, push the real path of it to stack in settings and 
    change current directory to there.
    """
    new_path = os.path.join(get_path(settings), path)
    nest_path_absolute(settings, new_path)


def unnest_path(settings):
    """
    Pop the path from stack in settings and
    change current directory to current top path of stack.
    """
    pop_path(settings)
    ensure_path(settings)


def validate(settings):
    """
    Perform a calibrated measurement of execution time and 
    calculate the error.
    """
    nest_path_from_root(settings, '/data/bin/')

    real_time_us = 0
    overhead_time = validate_single('do_nothing', real_time_us, 0)

    real_time_us = 500000
    validate_single('atax_base', real_time_us, overhead_time)
    unnest_path(settings)


def validate_default(settings):
    """
    Perform validation on set of time-measurement programs and report errors.
    """
    nest_path_from_root(settings, '/data/bin/')
    
    for i in range(7):
        real_time_us = 10**i
        s = 'usleep_{0}'.format(real_time_us)
        validate_single(s, real_time_us / 10**6, overhead_time)
    unnest_path(settings)


def validate_single(s, real_time, overhead_time):
    result = calibrate(s)
    measured_time = result.time - overhead_time
    error = abs(measured_time - real_time)
    relative_error = error / measured_time
    print ValidationResult(real_time, measured_time, error, relative_error)
    return real_time


def make_running_function(command):
    """Make a function which runs the specified command."""
    def run():
        p = sp.Popen(command.split(), 
                     stdout=sp.PIPE, 
                     stderr=sp.PIPE)
        return p.communicate()
    return run


def calibrate(command):
    """Calibrate execution of command until measurement is accurate enough."""
    n = 0
    t = 0
    d_rel = 1
    print "Begin"
    while (t < 1) and (d_rel > 0.05):
        sys.stderr.write('.')
        n += 1
        number = 10**(n)
        result = timeit.repeat(stmt='run()', 
                               setup=definition.format(command=command), 
                               number=number,
                               repeat=3)
        # t = np.average(np.array(result))
        t = min(result)
        d = np.std(np.array(result))
        d_rel = d / t
        # print t, t / number, d, d_rel, n, result
    sys.stderr.write('\n')
    return CalibrationResult(t, t / number, d, d_rel, number, result)


def convert_input_to_settings(input):
    program_name, benchmark_root_dir = \
        os.path.split(os.path.realpath(Input[benchmark_source_dir]))
    framework_root_dir, _ = os.path.split(os.path.realpath(__file__))
    settings = Settings(program_name=program_name,
                        benchmark_root_dir=benchmark_root_dir,
                        framework_root_dir=framework_root_dir)
    return settings, build_settings, run_settings


def perform_experiment(iterations=None):
    """Perform experiment with given number of iterations."""
    if iterations is None:
        iterations = 1

    build_reference(settings)
    build_timed(settings)

    for i in range(iterations):
        run_reference(settings)
        run_timed(settings)


def print_experiments(db):
    """Print all the experiments."""
    experiments = db.view('experiment/all')
    for e in experiments.all():
        print 'Experiment:'
        print 'Build:', e['value']['command_build']
        print 'Run:', e['value']['command_run']
        print 'Date & time:', e['value']['datetime']


def setup_database(settings):
    """Setup the database."""
    server = ck.Server()
    db = server.get_or_create_db('experiment')
    Experiment.set_db(db)
    path_db = settings.framework_root_dir + \
              '/couch'
    push(path_db, db)
    return server, db


def create_local_settings(settings):
    """Create local settings from global."""
    local_settings = dict()
    local_settings['program_source'] = '{program_name}.c'.format(
        **{'program_name': settings.program_name})
    local_settings.update(settings._asdict())
    return local_settings


def prepare_command_build_reference(settings):
    """Prepare command for building of reference version of benchmark."""
    command = tw.dedent("""
        {compiler} -O0 -I utilities -I {benchmark_source_dir} 
        utilities/polybench.c {benchmark_source_dir}/{program_source} 
        -DPOLYBENCH_DUMP_ARRAYS 
        -o ./bin/{program_name}_ref""").translate(None, '\n').format(
        **settings)
    return command


def prepare_command_build_timed(settings):
    """Prepare command for building of timed version of benchmark."""
    command = tw.dedent("""
        {compiler} {base_opt} -I utilities 
        -I {benchmark_source_dir} utilities/polybench.c 
        {benchmark_source_dir}/{program_source} -DPOLYBENCH_TIME 
        -o ./bin/{program_name}_time""").translate(None, '\n').format(
        **settings)
    return command


def prepare_command_run_reference(settings):
    """Prepare command for running the reference version of program."""
    command = tw.dedent("""
        ./bin/{program_name}_ref 1>./output/{program_name}_ref.out 
        2>./output/{program_name}_ref.err""").translate(None, '\n').format(
        **settings._asdict())
    return command


def prepare_command_run_timed(settings):
    """Prepare command for running the timed version of program."""
    command = tw.dedent("""
        ./bin/{program_name}_time 1>./output/{program_name}_time.out 
        2>./output/{program_name}_time.err""").translate(None, '\n').format(
        **settings._asdict())
    return command


def build_reference(settings):
    """Build the reference version of the benchmark."""
    local_settings = create_local_settings(settings)
    command = prepare_command_build_reference(local_settings)
    bin_dir = os.path.join(local_settings['framework_root_dir'], '/data/')
    os.chdir(bin_dir)
    print os.path.realpath(os.path.curdir)
    print command
    sp.call('mkdir bin'.split())
    sp.check_call(command.split())


def build_timed(settings):
    """Build the timed version of the benchmark."""
    local_settings = create_local_settings(settings)
    command = prepare_command_build_timed(local_settings)
    bin_dir = os.path.join(local_settings['framework_root_dir'], '/data/')
    os.chdir(bin_dir)
    print os.path.realpath(os.path.curdir)
    print command
    sp.call('mkdir bin'.split())
    sp.check_call(command.split())


def run_reference(settings):
    """Run the reference version of program."""
    command = prepare_command_run_reference(settings)
    print command
    proc = sp.Popen(command.split(), stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = proc.communicate()
    experiment = Experiment(
        command_build=None,
        command_run=command,
        stderr=stderr,
        stdout=stdout,
        datetime=dt.datetime.utcnow())
    experiment.save()


def run_timed(settings):
    """Run the timed version of program."""
    command = prepare_command_run_timed(settings)
    print command
    proc = sp.Popen(command.split(), stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = proc.communicate()
    experiment = Experiment(
        command_build=None,
        command_run=command,
        stderr=stderr,
        stdout=stdout,
        datetime=dt.datetime.utcnow())
    experiment.save()


if __name__ == '__main__':
    main()
