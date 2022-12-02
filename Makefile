.PHONY: run

all: install run

install: 
	julia --project=. -e "import Pkg; Pkg.instantiate()" 
	julia --project=. ./benchmark/ToQUBO/create_sysimage.jl

	pip install virtualenv

run:
	julia --project=. --sysimage ./benchmark/ToQUBO/sysimage ./benchmark/ToQUBO/tsp.jl --run

	# PyQUBO 
	virtualenv ./benchmark/pyqubo
	./benchmark/pyqubo/Scripts/activate                 
	pip install pyqubo==1.3.1
	pip install pandas
	python ./benchmark/pyqubo/tsp.py
	deactivate

	# PyQUBO 0.4.0
	virtualenv benchmark/pyqubo_040
	./benchmark/pyqubo_040/Scripts/activate                 
	pip install pyqubo==0.4.0
	pip install pandas
	python ./benchmark/pyqubo_040/tsp.py
	deactivate

plot:
	python ./benchmark/plot.py
