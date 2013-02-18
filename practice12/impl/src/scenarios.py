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
from settings import *
from context import *
from system import *

def cpdh_run(context):
    """Run scenario cpdh (see module docstring for description)."""
    dataset_sizes = ["MINI_DATASET", "SMALL_DATASET", "STANDARD_DATASET",
                     "LARGE_DATASET", "EXTRALARGE_DATASET"]
    settings = context.settings
    for size in dataset_sizes:
        settings.define_build_settings('src','-D{0}'.format(size))
        settings.build_settings.compiler = 'gcc'
        settings.build_settings.base_opt = '-O2'
        settings.build_settings.other_flags = '-I/home/constantius/diploma/'\
            'practice12/impl/data/sources/polybench-c-3.2/utilities '\
            'utilities/polybench.c -D{0}'.format(size)
        perform_experiment(context)


def cpdh_main():
    """Run initialization and scenario."""
    context = set_up('2mm')
    cpdh_run(context)
    tear_down(context)