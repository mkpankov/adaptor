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
1. `[×]` Prepare extensive search scenario. Doing statistics on 5 samples is laughable. We have to have at least ~100 of them. We need to launch program multiple times with ~random dataset sizes.
1. `[×]` Make the system setup not change the current directory.
1. `[×]` Consider the multiple programs with source code features design.
	* I currently think it's not necessary as it would duplicate the functionality. Better focus at model building.
1. `[-]` Think over the workflow. It is as follows.
	* Overall, it's postponed till we have at least locally working system.
	1. `[ ]` Data is collected until certain number of experiments is performed.
	1. `[ ]` Model is learned on these experiments. It's as simple as possible. Since source code features and optimization flags present very big amount of features, it will possibly lead to overfitting. To avoid that, we should consider the use of aggregated features (like level of optimizations instead of individual ones). The model is either of two.
		* This model should take into account the hardware-software platform, dataset size and guess good compiler parameters to reach optimal performance.
		* This model should take into account the hardware-software platform, dataset size and make a prediction of performance given some fixed compiler settings.
	1. `[ ]` Search is directed using feature ranking — features ranked in top are explored first. However, the search existence itself should be reconsidered. Rather, just normal program launches should happen. Anyway, we then assume that some experiments were conducted the specified number of times. If we're lucky, we get new points in interesting area. System could tune settings automatically without notice to the user. It could piss him off, but it could be disabled at will. It would improve the search by searching in interesting area.
	1. `[ ]` New model is learned. Basically it's loop of experimenting and learning.
1. `[×]` Split CPU flags feature into many binary features.
	* It is converted to set of features when needed. Stored as string as previously.
	* `[=]` Think about convinient representation of compound feature such as this.
		* It is just a set of strings.
	* `[=]` Refactor the feature representation taking considerations of the above into account.
		* No need, converted will be used when needed.
1. `[-]` Introduce optimization flags parameters for compiler.
	* It's postponed since it would introduce too much complexity.
	* `[ ]` Split levels of optimization into separate options.
	* `[ ]` Think about aggregative feature of optimization level.
1. `[×]` Automate the collected data preparation for analysis.
1. `[×]` Launch extensive search.
1. `[×]` Prepare the experimental scenario of data analysis.
	* Possible platforms:
		* `[•]` [Scikit-learn](http://scikit-learn.org/stable/#). Seems to have that we need. Average documentation.
			* Documentation turned out to be quite good (has explanation of models). Has many regression models, especially isotonic one, which is possibly what is useful for us. Has an Ubuntu package.
			* Tutorial showed it's a decent package, although lacking easy visualization, which is present in Orange in many forms.
		* `[-]` [mlpy](http://mlpy.sourceforge.net/). Seems to have what we need. Best documentation.
			* Has a lot of regression models and decent Python-style documentation with examples (!). Has Ubuntu package.
		* `[-]` [PyML](http://pyml.sourceforge.net/). Seems to have what we need. Somewhat documented.
		* `[×]` [Orange](http://orange.biolab.si/). Has graphical interface. Maybe has what we need. Average documentation.
			* Orange turned out to be laggy and buggy (especially on Linux) and very poorly documented. Apart from that, it has a name which makes it impossible to Google for. It's graphical interactive version is barely usable. Maybe it's better for scripting however. We now will go with another option.
	* Scenario itself is trial to build regression model based on feature choice. Feature choice will be implemented to account for need of different models for different platforms, which is not obviously required per se.
	* Maybe doing an offline regression model building is not so useful. We should aim for online learning.
		* In general, the system should behave as a cloud service.
		* One thought is that we should periodically detect outliers for current model and re-learn it. When re-learning fails (as it will fail due to unexpected by current model observations), we add a new model, which is used with new examples. Outliers are removed from current model and new model is learn on them. The approach is flawed in detection of what outliers are actually unpredictable data, and what are just noise.
1. `[-]` Add automatic building of dummy program.
1. `[-]` Add dependency checking: numpy, recordtype, couchdb, couchdbkit, couchapp.
1. `[ ]` Add support of Windows.
1. `[ ]` Add support of building Polybench/GPU.
1. `[ ]` Perform experiments on GPU.

## Ideas ##

Logotype of the system should be a raptor, which is placed accurately between 'A' and 'd' of the title. It imposes wordplay and so on and it's cool.