SHELL         := /bin/bash
TOQUBO_BRANCH := master
PYTHON        := python3

.PHONY: run

all: install run

install: 
	julia --project=. -e 'import Pkg; Pkg.add(Pkg.PackageSpec(url="https://github.com/psrenergy/ToQUBO.jl.git", rev="$(TOQUBO_BRANCH)")); Pkg.instantiate()'
	julia --project=. ./benchmark/ToQUBO/create_sysimage.jl

	pip install virtualenv

run:
	# ToQUBO.jl
	julia --project=. --sysimage ./benchmark/ToQUBO/sysimage ./benchmark/ToQUBO/tsp.jl --run

	# PyQUBO 
	virtualenv ./benchmark/pyqubo
	source ./benchmark/pyqubo/bin/activate
	pip install -r ./benchmark/pyqubo/requirements.txt
	$(PYTHON) ./benchmark/pyqubo/tsp.py

	# PyQUBO 0.4.0
	virtualenv ./benchmark/pyqubo_040
	source ./benchmark/pyqubo_040/bin/activate
	pip install -r ./benchmark/pyqubo_040/requirements.txt
	$(PYTHON) ./benchmark/pyqubo_040/tsp.py

plot:
	# Plots
	virtualenv ./benchmark/plots
	source ./benchmark/plots/bin/activate
	pip install -r ./benchmark/plots/requirements.txt
	$(PYTHON) ./benchmark/plots/plot.py
