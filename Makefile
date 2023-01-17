JULIA-EXE     := julia
PYTHON-EXE    := python3
TOQUBO-BRANCH := master
SHELL         := /bin/bash

.PHONY: run plot

all: run plot

run:
	@chmod +x ./bash/julia-run.sh
	./bash/julia-run.sh $(JULIA-EXE) $(TOQUBO-BRANCH)

	@chmod +x ./bash/python-run.sh
	./bash/python-run.sh $(PYTHON-EXE)

plot:
	@chmod +x ./bash/plot-run.sh
	./bash/plot-run.sh $(PYTHON-EXE)

clean:
	@rm -f ./benchmark/**/results.*.csv
	@rm -f ./data/results.*.pdf