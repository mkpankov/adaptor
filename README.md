# Adaptor #

Contains 'Adaptor' self-tuning computing framework.

Author: Michael K. Pankov, graduate of Bauman Moscow State Technical University.

![logo](/adaptor/doc/pictures/logo.png?raw=true)

## Useful links ##

1. [Orange tutorial](http://wiki.sdakak.com/ml:getting-started-with-orange).
1. [Scikit-learn](http://scikit-learn.org/stable/#). Seems to have that we need. Average documentation.
	* Documentation turned out to be quite good (has explanation of models). Has many regression models, especially isotonic one, which is possibly what is useful for us. Has an Ubuntu package.
	* Tutorial showed it's a decent package, although lacking easy visualization, which is present in Orange in many forms.
1. [mlpy](http://mlpy.sourceforge.net/). Seems to have what we need. Best documentation.
	* Has a lot of regression models and decent Python-style documentation with examples (!). Has Ubuntu package.
1. [PyML](http://pyml.sourceforge.net/). Seems to have what we need. Somewhat documented.
1. [Orange](http://orange.biolab.si/). Has graphical interface. Maybe has what we need. Average documentation.
	* Current option.
	* Orange turned out to be laggy and buggy (especially on Linux) and very poorly documented. Apart from that, it has a name which makes it impossible to Google for. It's graphical interactive version is barely usable. Maybe it's better for scripting however. We now will go with another option.

## TODO ##
1. `[ ]` Fix the system setup changing current directory.
1. `[ ]` Add support of Windows.
1. `[ ]` Add support of Polybench/GPU.
1. `[ ]` Perform experiments on GPU.
1. `[-]` Think over the workflow. It is as follows.
	* Overall, it's postponed till we have at least locally working system.
	1. `[ ]` Data is collected until certain number of experiments is performed.
	1. `[ ]` Model is learned on these experiments. It's as simple as possible. Since source code features and optimization flags present very big amount of features, it will possibly lead to overfitting. To avoid that, we should consider the use of aggregated features (like level of optimizations instead of individual ones). The model is either of two.
		* This model should take into account the hardware-software platform, dataset size and guess good compiler parameters to reach optimal performance.
		* This model should take into account the hardware-software platform, dataset size and make a prediction of performance given some fixed compiler settings.
	1. `[ ]` Search is directed using feature ranking — features ranked in top are explored first. However, the search existence itself should be reconsidered. Rather, just normal program launches should happen. Anyway, we then assume that some experiments were conducted the specified number of times. If we're lucky, we get new points in interesting area. System could tune settings automatically without notice to the user. It could piss him off, but it could be disabled at will. It would improve the search by searching in interesting area.
	1. `[ ]` New model is learned. Basically it's loop of experimenting and learning.
	* Scenario itself is trial to build regression model based on feature choice. Feature choice will be implemented to account for need of different models for different platforms, which is not obviously required per se.
	* Maybe doing an offline regression model building is not so useful. We should aim for online learning.
		* In general, the system should behave as a cloud service.
		* One thought is that we should periodically detect outliers for current model and re-learn it. When re-learning fails (as it will fail due to unexpected by current model observations), we add a new model, which is used with new examples. Outliers are removed from current model and new model is learn on them. The approach is flawed in detection of what outliers are actually unpredictable data, and what are just noise.
1. `[-]` Add automatic building of dummy program.
1. `[-]` Add dependency checking: numpy, recordtype, couchdb, couchdbkit, couchapp.

## Ideas ##

Currently none.