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

def cpdh_run(context):
    """Run scenario cpdh (see module docstring for description)."""
    settings = Settings('2mm')
    context = Context(settings)
    dataset_sizes = ["MINI_DATASET", "SMALL_DATASET", "STANDARD_DATASET",
                     "LARGE_DATASET", "EXTRALARGE_DATASET"]
    for size in dataset_sizes:
        settings.define_build_settings('src','-D{0}'.format(size))
        perform_experiment(context)