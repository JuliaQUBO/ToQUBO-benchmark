# Detect OS
ifeq ($(OS), Windows_NT)
	OSNAME := Windows
else
	OSNAME := $(shell uname)
endif

ifeq ($(OSNAME), Windows)
	PYTHON      := python
	PYTHON-PIP  := pip
	SYSIMAGE    := sysimage.dll
	VENV-SCRIPT := Scripts/activate
else ifeq ($(OSNAME), Darwin) # OSX
	PYTHON      := python3
	PYTHON-PIP  := pip3
	SYSIMAGE    := sysimage.dylib
	VENV-SCRIPT := bin/activate
else
	PYTHON      := python3
	PYTHON-PIP  := pip3
	SYSIMAGE    := sysimage
	VENV-SCRIPT := bin/activate
endif

SHELL         := /bin/bash
TOQUBO_BRANCH := master

.PHONY: run perf plot

all: install run

install: 
	julia --proj -e 'import Pkg; Pkg.add(Pkg.PackageSpec(url="https://github.com/psrenergy/ToQUBO.jl.git", rev="$(TOQUBO_BRANCH)")); Pkg.instantiate()'
	julia --proj ./benchmark/ToQUBO/create_sysimage.jl

	$(PYTHON-PIP) install virtualenv

run:
	julia --project=. --sysimage ./benchmark/ToQUBO/$(SYSIMAGE) ./benchmark/ToQUBO/tsp.jl --run

	virtualenv ./benchmark/pyqubo
	source ./benchmark/pyqubo/$(VENV-SCRIPT)
	$(PYTHON-PIP) install -r ./benchmark/pyqubo/requirements.txt
	$(PYTHON) ./benchmark/pyqubo/tsp.py

	virtualenv ./benchmark/pyqubo_040
	source ./benchmark/pyqubo_040/$(VENV-SCRIPT)
	$(PYTHON-PIP) install -r ./benchmark/pyqubo_040/requirements.txt
	$(PYTHON) ./benchmark/pyqubo_040/tsp.py

plot:
	virtualenv ./benchmark/plots
	source ./benchmark/plots/bin/activate
	$(PYTHON-PIP) install -r ./benchmark/plots/requirements.txt
	$(PYTHON) ./benchmark/plots/plot.py

perf:
	julia --project=perf --sysimage ./benchmark/ToQUBO/$(SYSIMAGE) ./perf/tsp.jl --run
