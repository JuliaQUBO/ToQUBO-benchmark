JULIA  ?= julia
PYTHON ?= python3
VENV   ?= .venv
VENV_PYTHON ?= $(VENV)/bin/python
PIP    ?= $(VENV)/bin/pip
OPENQAOA_VENV   ?= .venv-openqaoa
OPENQAOA_PYTHON ?= $(OPENQAOA_VENV)/bin/python
OPENQAOA_PIP    ?= $(OPENQAOA_VENV)/bin/pip
SHELL  := /bin/bash
PAPER_BASELINE := archive/paper-v1
PUBLICATION_SAMPLES ?= 10
PUBLICATION_WARMUPS ?= 1
PUBLICATION_TIME_STATISTIC ?= min

.PHONY: install run run-publication run-publication-python run-publication-toqubo report plot plot-paper venv openqaoa-venv
.NOTPARALLEL: run

all: install run plot

venv:
	$(PYTHON) -m venv "$(VENV)"
	$(VENV_PYTHON) -m pip --version >/dev/null

openqaoa-venv:
	$(PYTHON) -m venv "$(OPENQAOA_VENV)"
	$(OPENQAOA_PYTHON) -m pip --version >/dev/null

install: install-plot install-pyqubo install-qubovert install-qiskit install-openqaoa install-amplify install-dwave install-toqubo

install-plot: venv
	@echo "Installing Plot Tools..."
	@if command -v latex >/dev/null 2>&1 && command -v dvipng >/dev/null 2>&1; then \
		echo "TeX plot tools already installed."; \
	else \
		sudo apt-get update; \
		sudo apt-get install -y texlive texlive-latex-extra cm-super dvipng; \
	fi
	$(PIP) install -r "./plot/requirements.txt"

install-pyqubo: venv
	@echo "Installing pyqubo..."
	$(PIP) install -r "./benchmark/pyqubo/requirements.txt"

install-qubovert: venv
	@echo "Installing qubovert..."
	$(PIP) install -r "./benchmark/qubovert/requirements.txt"

install-qiskit: venv
	@echo "Installing qiskit..."
	$(PIP) install -r "./benchmark/qiskit/requirements.txt"

install-openqaoa: openqaoa-venv
	@echo "Installing openqaoa..."
	$(OPENQAOA_PIP) install -r "./benchmark/openqaoa/requirements.txt"

install-amplify: venv
	@echo "Installing amplify..."
	$(PIP) install -r "./benchmark/amplify/requirements.txt"

install-dwave: venv
	@echo "Installing dwave..."
	$(PIP) install -r "./benchmark/dwave/requirements.txt"

install-toqubo:
	@echo "Installing ToQUBO.jl..."
	$(JULIA) --proj=benchmark/ToQUBO -e 'import Pkg; Pkg.instantiate();'

run: run-pyqubo run-qubovert run-qiskit run-openqaoa run-amplify run-dwave run-toqubo
	$(MAKE) report

run-publication:
	BENCHMARK_SAMPLES="$(PUBLICATION_SAMPLES)" \
	BENCHMARK_WARMUPS="$(PUBLICATION_WARMUPS)" \
	BENCHMARK_TIME_STATISTIC="$(PUBLICATION_TIME_STATISTIC)" \
	$(MAKE) run-publication-python run-publication-toqubo report

run-publication-python: venv openqaoa-venv
	@echo "Running Python publication benchmarks with isolated samples..."
	$(VENV_PYTHON) "./scripts/run_python_benchmark_isolated.py" pyqubo qubovert qiskit amplify dwave
	MPLCONFIGDIR="$${MPLCONFIGDIR:-/tmp/matplotlib-toqubo-benchmark}" $(OPENQAOA_PYTHON) "./scripts/run_python_benchmark_isolated.py" openqaoa

run-publication-toqubo: venv
	@echo "Running ToQUBO.jl publication benchmark..."
	$(JULIA) --proj=benchmark/ToQUBO "./benchmark/ToQUBO/benchmark.jl" --run

run-pyqubo: venv
	@echo "Running pyqubo..."
	$(VENV_PYTHON) -m benchmark.pyqubo

run-qubovert: venv
	@echo "Running qubovert..."
	$(VENV_PYTHON) -m benchmark.qubovert

run-qiskit: venv
	@echo "Running qiskit..."
	$(VENV_PYTHON) -m benchmark.qiskit

run-openqaoa: openqaoa-venv
	@echo "Running openqaoa..."
	MPLCONFIGDIR="$${MPLCONFIGDIR:-/tmp/matplotlib-toqubo-benchmark}" $(OPENQAOA_PYTHON) -m benchmark.openqaoa

run-amplify: venv
	@echo "Running amplify..."
	$(VENV_PYTHON) -m benchmark.amplify

run-dwave: venv
	@echo "Running dwave..."
	$(VENV_PYTHON) -m benchmark.dwave
	
run-toqubo: venv
	@echo "Running ToQUBO.jl..."
	$(JULIA) --proj=benchmark/ToQUBO "./benchmark/ToQUBO/benchmark.jl" --run

report: venv
	@echo "Writing benchmark report..."
	BENCHMARK_JULIA="$(JULIA)" \
	BENCHMARK_JULIA_VERSION="$$($(JULIA) --version)" \
	BENCHMARK_OPENQAOA_PYTHON="$(OPENQAOA_PYTHON)" \
	BENCHMARK_OPENQAOA_PYTHON_VERSION="$$($(OPENQAOA_PYTHON) --version 2>/dev/null || true)" \
	$(VENV_PYTHON) "./scripts/write_benchmark_report.py"

plot: venv
	@echo "Drawing Plots..."
	$(VENV_PYTHON) "./plot/plot.py"

plot-paper: venv
	@echo "Drawing Paper Plots..."
	$(VENV_PYTHON) "./plot/plot.py" --results-dir "$(PAPER_BASELINE)/benchmark" --output-dir "$(PAPER_BASELINE)/data"

clean:
	@rm -f ./benchmark/**/results*.csv
	@rm -f ./data/results*.pdf
	@rm -f ./data/results*.png
