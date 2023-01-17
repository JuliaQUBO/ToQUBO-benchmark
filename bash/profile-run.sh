#! /usr/bin/env bash

JULIA_EXE="$1"

PREFIX="./perf/"

function profile {
    ${JULIA_EXE} --proj=${PREFIX} -i "${PREFIX}/profile.jl"

    return 0
}