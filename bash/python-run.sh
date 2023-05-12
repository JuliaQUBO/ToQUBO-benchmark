#! /usr/bin/env bash

PYTHON_EXE="$1"

PREFIX="./benchmark/"

# Benchmarks:
# - PyQUBO   (latest)
# - Qiskit   (0.41)
# - qubovert (latest)
# Every benchmark must produce the following files:
# - results.tsp.csv
# - results.npp.csv
# There must be at least two columns on each file:
# - `nvar` (int)
# - `time` (float)

function benchmark {
    echo "Installing ${1}..."
    ${PYTHON_EXE} -m pip install -r "${PREFIX}/${1}/requirements.txt"

    echo "Running ${1}..."
    ${PYTHON_EXE} -m benchmark.${1}

    echo "Finished ${1}"

    return 0
}

benchmark "pyqubo"
benchmark "qubovert"
benchmark "qiskit"
benchmark "openqaoa"
benchmark "amplify"
