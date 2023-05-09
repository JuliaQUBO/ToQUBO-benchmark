#! /usr/bin/env bash

PYTHON_EXE="$1"

PREFIX="./plot/"

function plot {
    echo "Installing Plot Tools"
	sudo apt install texlive texlive-latex-extra cm-super dvipng
	${PYTHON_EXE} -m pip install --user -r "${PREFIX}/requirements.txt"

	echo "Drawing Plots"
	${PYTHON_EXE} "${PREFIX}/plot.py"

	return 0
}

plot
