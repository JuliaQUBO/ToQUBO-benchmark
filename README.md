# ToQUBO-benchmark

Benchmarks for a paper on [ToQUBO.jl](https://github.com/psrenergy/ToQUBO.jl)


## Setup
### ToQUBO 
Initialize the Julia environments as follows:
``` ps
$ julia --project=. -e "import Pkg; Pkg.instantiate()" 
$ julia --project=. benchmark/ToQUBO/create_sysimage.jl
``` 


### PyQUBO
To run PyQUBO experiments you first need to install [virtualenv](https://github.com/pypa/virtualenv):
``` ps
$ pip install virtualenv
``` 





## Run benchmark experiments

### ToQUBO
``` ps
$ julia --project=. --sysimage .\benchmark\ToQUBO\sysimage .\benchmark\ToQUBO\tsp.jl --run
```

### PyQUBO

PyQUBO is tested with two different versions(1.3.1 and 0.4.0), so you need to use two different environments:
### PyQUBO - latest
```ps
$ virtualenv benchmark\pyqubo
$ .\benchmark\pyqubo\Scripts\activate                 
$ pip install pyqubo==1.3.1
$ pip install pandas
$ python .\benchmark\pyqubo\tsp.py
``` 

### PyQUBO - 0.4.0
```ps
$ virtualenv benchmark\pyqubo_040
$ .\benchmark\pyqubo_040\Scripts\activate                 
$ pip install pyqubo==0.4.0
$ pip install pandas
$ python .\benchmark\pyqubo_040\tsp.py
``` 

To exit an environment run the following:
``` ps
$ deactivate
```

## Visualize benchmark results
The results are saved on `.csv` files, present in the folders for each experiment. To visualize them, do the following:
``` ps
$ python .\benchmark\plot.py
```
Note: to plot our graph, we use `matplotlib`, `pandas` and `scienceplots`