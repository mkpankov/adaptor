#!/usr/bin/env python

"""Run experiment with specified program with given compilers."""

import os
import subprocess as sp
import textwrap as tw
import datetime as dt
import couchdbkit as ck
from couchdbkit.designer import push
import recordtype as rt
import collections as cl


class Experiment(ck.Document):
    command_build = ck.StringProperty()
    command_run = ck.StringProperty()
    stdout = ck.StringProperty()
    stderr = ck.StringProperty()
    datetime = ck.DateTimeProperty()


Input = cl.namedtuple('Input',
    'benchmark_source_dir compiler base_opt')
Settings = rt.recordtype('Settings', 
    'program_name benchmark_root_dir framework_root_dir')
BuildSettings = rt.recordtype('BuildSettings',
    'compiler base_opt optimization_flags other_flags '
    'benchmark_source_dir')
RunSettings = rt.recordtype('RunSettings',
    'benchmark_bin_dir')


def main():
    """Invoke all necessary builds and experiments."""

    settings = Settings(compiler='gcc', base_opt='-O3', 
        program_name='atax', 
        benchmark_root_dir='../data/sources/polybench-c-3.2',
        benchmark_source_dir='linear-algebra/kernels/atax',
        framework_root_dir=os.path.realpath('..'))
    settings.benchmark_root_dir = os.path.realpath(
        settings.benchmark_root_dir)
    server, db = setup_database(settings)

    perform_experiment()

    print_experiments(db)


def convert_input_to_settings(input):
    """Process user input (command line arguments) and return settings."""
    
    program_name, benchmark_root_dir = \
        os.path.split(os.path.realpath(Input[benchmark_source_dir]))
    framework_root_dir, _ = os.path.split(os.path.realpath(__file__))

    settings = Settings(program_name=program_name,
        benchmark_root_dir=benchmark_root_dir,
        framework_root_dir=framework_root_dir)

    build_settings = BuildSettings(compiler=Input[compiler],
        base_opt=Input[base_opt],
        benchmark_source_dir=Input[benchmark_source_dir])

    benchmark_bin_dir = os.path.join(framework_root_dir, '/data/bin/')
    run_settings = RunSettings(benchmark_bin_dir=benchmark_bin_dir)
    
    return settings, build_settings, run_settings


def handle_ref_timed_stdout(stdout):
    """Process the stdout."""

    pass


def handle_ref_timed_stderr(stderr):
    """Process the stderr."""

    pass


def perform_experiment(iterations=None):
    """Perform experiment with given number of iterations."""

    iterations = 1 if iterations is None
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
    os.chdir(local_settings['benchmark_root_dir'])
    print os.path.realpath(os.path.curdir)
    print command
    sp.call('mkdir bin'.split())
    sp.check_call(command.split())


def build_timed(settings):
    """Build the timed version of the benchmark."""

    local_settings = create_local_settings(settings)
    command = prepare_command_build_timed(local_settings)
    os.chdir(local_settings['benchmark_root_dir'])
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
