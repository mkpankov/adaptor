# Diploma #

It's a diploma project of me, Michael Pankov, student of 6th course at Bauman Moscow State Technical University.
Contains 'Adaptor' self-tuning computing framework.

## TODO ##

1. `[×]` Migrate to CouchDB cloud hosting. [CloudAnt](https://cloudant.com/) was chosen.
1. `[×]` Prepare system information collection module.
1. `[×]` Make the system search for needed program, not bail out right after not finding it in root of benchmark.
1. `[×]` Prepare the experimental scenario of data collection.
1. `[×]` Add the CPU name collection to Probe.
1. `[×]` Choose a more quickly running program.
	* symm was chosen: ./polybench-c-3.2/linear-algebra/kernels/symm.
1. `[ ]` Add the «Experiment series» field to ExperimentDocument.
1. `[ ]` Prepare the experimental scenario of data analysis.
	* Possible platforms:
		* `[ ]` [Scikit-learn](http://scikit-learn.org/stable/#). Seems to not have that we need. Average documentation.
		* `[ ]` [mlpy](http://mlpy.sourceforge.net/). Seems to have what we need. Decent documentation.
		* `[ ]` [PyML](http://pyml.sourceforge.net/). Seems to have what we need. Best documentation.
		* `[•]` [Orange](http://orange.biolab.si/). Has graphical interface. Maybe has what we need. Average documentation.

1. `[ ]` Perform 10 runs several times, each with different settings: some with one dataset size, some with other; some with one hardware, some with other. It's hard to get different hardware for me so I must think of emulation (i.e. setting of CPU frequency).
	* Emulation proved to be not an option since VM doesn't effectively support hardware adjustment. I now aim for usage of laptop and PC as 2 different machines.
1. `[ ]` Add automatic building of dummy program.
1. `[ ]` Add dependency checking: numpy, recordtype, couchdb, couchdbkit, couchapp.

## Ideas ##

Logotype of the system should be a raptor, which is placed accurately between 'A' and 'd' of the title. It imposes wordplay and so on and it's cool.