JULIA  := julia
PYTHON := python3
SHELL  := /bin/bash

.PHONY: install run plot

all: install run plot

install: install-plot install-pyqubo install-qubovert install-qiskit install-openqaoa install-amplify install-toqubo

install-plot:
	@echo "Installing Plot Tools..."
	@sudo apt install texlive texlive-latex-extra cm-super dvipng
	$(PYTHON) -m pip install --user -r "./plot/requirements.txt"

install-pyqubo:
	@echo "Installing pyqubo..."
	$(PYTHON) -m pip install --user -r "./benchmark/pyqubo/requirements.txt"

install-qubovert:
	@echo "Installing qubovert..."
	$(PYTHON) -m pip install --user -r "./benchmark/qubovert/requirements.txt"

install-qiskit:
	@echo "Installing qiskit..."
	$(PYTHON) -m pip install --user -r "./benchmark/qiskit/requirements.txt"

install-openqaoa:
	@echo "Installing openqaoa..."
	$(PYTHON) -m pip install --user -r "./benchmark/openqaoa/requirements.txt"

install-amplify:
	@echo "Installing amplify..."
	$(PYTHON) -m pip install --user -r "./benchmark/amplify/requirements.txt"

install-toqubo:
	@echo "Installing ToQUBO.jl..."
	$(JULIA) --proj=benchmark/ToQUBO -e 'import Pkg; Pkg.add(;name="ToQUBO", version=v"0.1.6"); Pkg.instantiate();'
	
	@echo "Creating sysimage..."
	$(JULIA) --proj=benchmark/ToQUBO "./benchmark/ToQUBO/create_sysimage.jl"

run: run-pyqubo run-qubovert run-qiskit run-openqaoa run-amplify

run-pyqubo:
	@echo "Running pyqubo..."
	$(PYTHON) -m benchmark.pyqubo

run-qubovert:
	@echo "Running qubovert..."
	$(PYTHON) -m benchmark.qubovert

run-qiskit:
	@echo "Running qiskit..."
	$(PYTHON) -m benchmark.qiskit

run-openqaoa:
	@echo "Running openqaoa..."
	$(PYTHON) -m benchmark.openqaoa

run-amplify:
	@echo "Running amplify..."
	$(PYTHON) -m benchmark.amplify
	
run-toqubo:
	@echo "Running ToQUBO.jl..."
	$(JULIA) --proj=benchmark/ToQUBO --sysimage "./benchmark/ToQUBO/sysimage" "./benchmark/ToQUBO/benchmark.jl" --run

plot:
	@echo "Drawing Plots..."
	$(PYTHON) "./plot/plot.py"

clean:
	@rm -f ./benchmark/**/results*.csv
	@rm -f ./data/results*.pdf
	@rm -f ./data/results*.png