#! /usr/bin/env bash

PYTHON_EXE="$1"
JULIA_EXE="$2"

PREFIX="./report/"

function report {
    echo "Installing..."
    ${PYTHON_EXE} -m pip install -r "${PREFIX}/requirements.txt"

    echo "Running..."
    ${PYTHON_EXE} "${PREFIX}/report.py" "${JULIA_EXE}"

    echo "Finished"    

    return 0
}

report
