PYTHON        := python3
PYTHON-PIP    := pip3
SYSIMAGE      := sysimage
VENV-SCRIPT   := bin/activate
VENV-CMD      := virtualenv
SOURCE-CMD    := source
SHELL         := /bin/bash
TOQUBO_BRANCH := master

.PHONY: run plot

all: run plot

run: install-run run-julia run-python

install-run: install-venv

run-julia: toqubo

toqubo:
	@echo "Installing ToQUBO.jl"
	@julia --proj -e 'import Pkg; Pkg.add(Pkg.PackageSpec(url="https://github.com/psrenergy/ToQUBO.jl.git", rev="$(TOQUBO_BRANCH)")); Pkg.instantiate()'
	@julia --proj ./benchmark/ToQUBO/create_sysimage.jl

	@echo "Running ToQUBO.jl"
	@julia --project=. --sysimage ./benchmark/ToQUBO/$(SYSIMAGE) ./benchmark/ToQUBO/tsp.jl --run

run-python: qubovert pyqubo-latest pyqubo-040

qubovert:
	@echo "Installing qubovert"
	@$(VENV-CMD) ./benchmark/qubovert
	@$(SOURCE-CMD) ./benchmark/qubovert/$(VENV-SCRIPT)
	@pip install -r ./benchmark/qubovert/requirements.txt

	@echo "Running qubovert"
	@$(PYTHON) ./benchmark/qubovert/tsp.py

pyqubo-latest:
	@echo "Installing PyQUBO (v1.4.0)"
	@$(VENV-CMD) ./benchmark/pyqubo
	@$(SOURCE-CMD) ./benchmark/pyqubo/$(VENV-SCRIPT)
	@pip install -r ./benchmark/pyqubo/requirements.txt

	@echo "Running PyQUBO (v1.4.0)"
	@$(PYTHON) ./benchmark/pyqubo/tsp.py

pyqubo-040:
	@echo "Installing PyQUBO (v0.4.0)"
	@$(VENV-CMD) ./benchmark/pyqubo_040
	@$(SOURCE-CMD) ./benchmark/pyqubo_040/$(VENV-SCRIPT)
	@pip install -r ./benchmark/pyqubo_040/requirements.txt

	@echo "Running PyQUBO (v0.4.0)"
	@$(PYTHON) ./benchmark/pyqubo_040/tsp.py

plot: install-plot draw-plot

install-plot: install-venv install-latex

draw-plot:
	@echo "Installing Plot Tools"
	@$(VENV-CMD) ./benchmark/plots
	@$(SOURCE-CMD) ./benchmark/plots/$(VENV-SCRIPT)
	@pip install -r ./benchmark/plots/requirements.txt

	@echo "Drawing Plots"
	@$(PYTHON) ./benchmark/plots/plot.py

install-venv:
	$(PYTHON-PIP) install virtualenv

install-latex:
	sudo apt install texlive texlive-latex-extra cm-super dvipng
