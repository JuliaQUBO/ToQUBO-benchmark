#! /usr/bin/env bash

JULIA_EXE="$1"
BRANCH="$2"

GIT_REPO="https://github.com/psrenergy/ToQUBO.jl.git"
PREFIX="./benchmark/ToQUBO/"

# Benchmarks:
# - ToQUBO
# Every benchmark must produce the following files:
# - results.tsp.csv
# - results.npp.csv
# There must be at least two columns on each file:
# - `nvar` (int)
# - `time` (float)

function benchmark {
    echo "Installing ToQUBO.jl..."
    ${JULIA_EXE} --proj -e "
        import Pkg;
        Pkg.add(Pkg.PackageSpec(url=\"${GIT_REPO}\", rev=\"${BRANCH}\"));
        Pkg.instantiate();
    "

    echo "Creating sysimage..."
    ${JULIA_EXE} --proj=${PREFIX} "${PREFIX}/create_sysimage.jl"

    echo "Running ToQUBO.jl..."
    ${JULIA_EXE} --proj=${PREFIX} --sysimage "${PREFIX}/sysimage" "${PREFIX}/benchmark.jl" --run

    echo "Finished ToQUBO.jl"

    return 0
}

benchmark
