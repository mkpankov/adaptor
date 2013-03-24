It is wider problem than you would think. Not just classification. Actually, classification is not the main reason for no collective optimization in production compilers.

It might be wrong to present this task as ML for compilers, but now it's more fully understood by me and it's actually collective optimization more than anything else.

1. There are a lot of infrastructure and engineering challenges not overcome by anyone
	1. No common setup
	2. No convinient way to exchange results
	3. No common database
2. Computer systems are barely tunable because of usual usage of heuristic and default optimizations, which just offer some trade-offs believed to behave good in many cases.
3. Extraction of information is no easy task: it has to deal with program, dataset, compiler, OS and hardware platform.
4. Formalization of features, optimizations and particular choices is hard and requires profound understanding of computer architecture and a lot of expert work to build performance model in the first place (so that it could be tuned after that).
5. There're a huge amount of different combinations and search space is enormous. Therefore, collective optimization is needed, which is done via framework.
So far it were mainly engineering challenges.
6. Employ ML to choose needed optimizations and/or predict performance.

We

1. Have to make computer systems tunable and be able to extract all possible information at all levels
(difficult engineering task)
2. Formalize properties (features), characteristics and choices
3. Explore large optimization spaces and collect/process huge amount of data
4. Only then apply various classification and predictive modeling techniques

No one payed attention to points 1-3, only 4, and experiments are not reproducible and not systematic.

Proposal is:
1. Make available collection of features.
2. Perform formalization of features, characteristics and choices.
3. Build performance model.
4. Employ search with some model.
5. Employ ML.