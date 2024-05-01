JULIA  := julia
PYTHON := python3
PIP    := ~/.local/bin/pip
SHELL  := /bin/bash

.PHONY: install run plot

all: install run plot

venv:
	$(PYTHON) -m venv ~/.local --system-site-packages

install: install-plot install-pyqubo install-qubovert install-qiskit install-openqaoa install-amplify install-dwave install-toqubo

install-plot: venv
	@echo "Installing Plot Tools..."
	@sudo apt install texlive texlive-latex-extra cm-super dvipng
	$(PIP) install --user -r "./plot/requirements.txt"

install-pyqubo: venv
	@echo "Installing pyqubo..."
	$(PIP) install --user -r "./benchmark/pyqubo/requirements.txt"

install-qubovert: venv
	@echo "Installing qubovert..."
	$(PIP) install --user -r "./benchmark/qubovert/requirements.txt"

install-qiskit: venv
	@echo "Installing qiskit..."
	$(PIP) install --user -r "./benchmark/qiskit/requirements.txt"

install-openqaoa: venv
	@echo "Installing openqaoa..."
	$(PIP) install --user -r "./benchmark/openqaoa/requirements.txt"

install-amplify: venv
	@echo "Installing amplify..."
	$(PIP) install --user -r "./benchmark/amplify/requirements.txt"

install-dwave: venv
	@echo "Installing dwave..."
	$(PIP) install --user -r "./benchmark/dwave/requirements.txt"

install-toqubo:
	@echo "Installing ToQUBO.jl..."
	$(JULIA) --proj=benchmark/ToQUBO -e 'import Pkg; Pkg.add(;name="ToQUBO", version=v"0.1.6"); Pkg.instantiate();'
	
	@echo "Creating sysimage..."
	$(JULIA) --proj=benchmark/ToQUBO "./benchmark/ToQUBO/create_sysimage.jl"

run: run-pyqubo run-qubovert run-qiskit run-openqaoa run-amplify run-dwave run-toqubo

run-pyqubo: venv
	@echo "Running pyqubo..."
	$(PYTHON) -m benchmark.pyqubo

run-qubovert: venv
	@echo "Running qubovert..."
	$(PYTHON) -m benchmark.qubovert

run-qiskit: venv
	@echo "Running qiskit..."
	$(PYTHON) -m benchmark.qiskit

run-openqaoa: venv
	@echo "Running openqaoa..."
	$(PYTHON) -m benchmark.openqaoa

run-amplify: venv
	@echo "Running amplify..."
	$(PYTHON) -m benchmark.amplify

run-dwave: venv
	@echo "Running dwave..."
	$(PYTHON) -m benchmark.dwave
	
run-toqubo: venv
	@echo "Running ToQUBO.jl..."
	$(JULIA) --proj=benchmark/ToQUBO --sysimage "./benchmark/ToQUBO/sysimage" "./benchmark/ToQUBO/benchmark.jl" --run

plot: venv
	@echo "Drawing Plots..."
	$(PYTHON) "./plot/plot.py"

clean:
	@rm -f ./benchmark/**/results*.csv
	@rm -f ./data/results*.pdf
	@rm -f ./data/results*.png