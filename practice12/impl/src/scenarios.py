# coding: utf-8

"""
Scenario module. Implements some research scenarios in a relatively 
high-level way.

Currently it is intended to have 2 main scenarios:
*   codename cpdh (semantic is "collect-performance-dataset-hardware"):
    *   collect data on performance of single program using different dataset 
sizes. This should be run on different hardware platforms to provide data to 
analyze and build a classifier on;
*   codename mpdh (semantic is "model-performance-dataset-hardware"):
    *   build a model of performance of hardware platform depending on dataset 
size. Analyze it and determine if new features should be added to make model
more adequate. Also determine which features should be added, if any.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

import ipdb
import random

from settings import *
from context import *
from system import *

def cpdh_run(context):
    """Run scenario cpdh (see module docstring for description)."""
    dataset_sizes = [2**x for x in range(1,12)]

    settings = context.settings
    for size in dataset_sizes:
        settings.define_build_settings('src','-D{0}'.format(size))
        settings.build_settings.compiler = 'gcc'
        settings.build_settings.base_opt = '-O2'
        settings.build_settings.other_flags = '-I{1}'\
            '/data/sources/polybench-c-3.2/utilities '\
            'utilities/polybench.c -DNI={0} -DNJ={0}'.format(
                size, context.paths_manager.framework_root_dir)
        perform_experiment(context)


def cpdh_explore(context, trials=10, dataset_min=2, dataset_max=1024):
    """Run exploration scenario."""
    settings = context.settings

    for i in range(trials):
        size = random.randint(dataset_min, dataset_max)
        settings.define_build_settings('src','')
        settings.build_settings.compiler = 'gcc'
        settings.build_settings.base_opt = '-O2'
        settings.build_settings.other_flags = '-I{1}'\
            '/data/sources/polybench-c-3.2/utilities '\
            'utilities/polybench.c -DNI={0} -DNJ={0}'.format(
                size, context.paths_manager.framework_root_dir)
        perform_experiment(context)


def cpdh_main():
    """Run initialization and scenario."""
    context = set_up('symm', False, 'series2')
    cpdh_explore(context, trials=10, dataset_min=2, dataset_max=1024)
    tear_down(context)


def mpdh_main():
    """Run initialization and scenario."""
    context = set_up('symm', False, 'series2')
    plot()
    tear_down(context)


def plot():
    v = ExperimentDocument.view('adaptor/experiment-all')
    l = []
    for doc in v:
        if doc.series == 'series2':
            l.append(doc)
    print l