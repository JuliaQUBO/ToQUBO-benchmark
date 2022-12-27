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

run: run-python run-julia

run-julia:
	@./bash/run-julia

run-python:
	@./bash/run-python

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
