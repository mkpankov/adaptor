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
1. `[×]` Add the «Experiment series» field to ExperimentDocument.
1. `[×]` Complete the Orange tutorial.
	* [This](http://wiki.sdakak.com/ml:getting-started-with-orange)
1. `[×]` Complete the sklearn tutorial.
1. `[×]` Put relative path to headers at scenarios.py:38.
1. `[×]` Add hashing of entire executable as part of Experiment.
1. `[ ]` Prepare extensive search scenario. Doing statistics on 5 samples is laughable. We have to have at least ~100 of them. We need to launch program multiple times with ~random dataset sizes.
1. `[ ]` Launch extensive search.
1. `[ ]` Prepare the experimental scenario of data analysis.
	* Possible platforms:
		* `[•]` [Scikit-learn](http://scikit-learn.org/stable/#). Seems to have that we need. Average documentation.
			* Documentation turned out to be quite good (has explanation of models). Has many regression models, especially isotonic one, which is possibly what is useful for us. Has an Ubuntu package.
			* Tutorial showed it's a decent package, although lacking easy visualization, which is present in Orange in many forms.
		* `[ ]` [mlpy](http://mlpy.sourceforge.net/). Seems to have what we need. Best documentation.
			* Has a lot of regression models and decent Python-style documentation with examples (!). Has Ubuntu package.
		* `[ ]` [PyML](http://pyml.sourceforge.net/). Seems to have what we need. Somewhat documented.
		* `[•]` [Orange](http://orange.biolab.si/). Has graphical interface. Maybe has what we need. Average documentation.
			* Orange turned out to be laggy and buggy (especially on Linux) and very poorly documented. Apart from that, it has a name which makes it impossible to Google for. It's graphical interactive version is barely usable. Maybe it's better for scripting however. We now will go with another option.
	* Scenario itself is trial to build regression model based on feature choice. Feature choice will be implemented to account for need of different models for different platforms, which is not obviously required per se.
	* Maybe doing an offline regression model building is not so useful. We should aim for online learning.
		* In general, the system should behave as a cloud service.
		* One thought is that we should periodically detect outliers for current model and re-learn it. When re-learning fails (as it will fail due to unexpected by current model observations), we add a new model, which is used with new examples. Outliers are removed from current model and new model is learn on them. The approach is flawed in detection of what outliers are actually unpredictable data, and what are just noise.
1. `[ ]` Add automatic building of dummy program.
1. `[ ]` Add dependency checking: numpy, recordtype, couchdb, couchdbkit, couchapp.

## Ideas ##

Logotype of the system should be a raptor, which is placed accurately between 'A' and 'd' of the title. It imposes wordplay and so on and it's cool.