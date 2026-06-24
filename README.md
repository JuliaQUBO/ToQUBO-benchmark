# ToQUBO-benchmark

Benchmarks for a paper on [QUBO.jl](https://github.com/JuliaQUBO/QUBO.jl)

[![arXiv](https://img.shields.io/badge/arXiv-2307.02577-b31b1b.svg)](https://arxiv.org/abs/2307.02577)

[![Benchmark Results](./data/results.png)](/)

## Archived paper results

The benchmark CSV files used for the paper are archived in
[`archive/paper-v1`](./archive/paper-v1). This baseline should stay fixed while
the top-level `benchmark/` and `data/` directories are modernized and rerun.

To redraw the paper plots from the archived CSV files:

```shell
$ make plot-paper
```

## Updating dependencies and results

Dependabot PRs should update dependency files only. They should not change
`archive/paper-v1`; the `verify` workflow checks that the archived files still
match their recorded hashes.

The top-level `benchmark/` and `data/` directories are the live benchmark
outputs. After merging dependency updates, rerun the benchmark intentionally
with the `toqubo-benchmark` workflow dispatch or a commit containing `[run]`.
The plot workflow will then redraw plots for the new live results.

If a future run needs to be preserved as another fixed reference point, add a new
archive directory such as `archive/modern-v1` instead of overwriting
`archive/paper-v1`.

## Current live result set

The top-level CSV files currently contain
`toqubo-0.5.1-qubotools-0.15.1-2026-06-24`, a diagnostic rerun of the ToQUBO
results after ToQUBO.jl v0.5.1 and QUBOTools.jl v0.15.1 were available from the
Julia General registry.
The other live package CSVs remain from `latest-stack-2026-06-19-rerun`. This
replaces the mixed-date latest-stack experiment from PR #11, but it is not
archived as a paper-style fixed reference point.

OpenQAOA is still excluded from the live run because `openqaoa==0.2.6` does not
resolve on Python 3.12. The historical OpenQAOA rows remain available under
`archive/paper-v1`.

The ToQUBO.jl benchmark uses `extract_qubo_backend` in
`benchmark/ToQUBO/problems.jl` to call the public `QUBOTools.backend(model)`
path added for ToQUBO-compiled JuMP models. This run uses registered releases:
ToQUBO.jl v0.5.1 and QUBOTools.jl v0.15.1. In the current TSP run, backend
extraction is 0.113 s of 1.967 s at 10,000 variables, so extraction is no
longer the dense TSP bottleneck. The 1,000-variable NPP row is 0.308 s,
including 0.002 s of backend extraction.

The live run provenance, package versions, CSV row counts, and SHA-256 hashes
are recorded in [`data/report.json`](./data/report.json).

The environment table below describes this diagnostic WSL2 run only. A future
authoritative archived baseline should be produced from the documented CI
matrix or should record its exact environment before being compared with the
archived paper baseline.

## How to reproduce the results

## Environment

| Linux  | Linux 6.6.114.1 WSL2 / x86_64 |
| :----: | :----------------------------: |
| Python | CPython 3.13.5                 |
| Julia  | julia version 1.12.6           |

## Packages

| Package             | Version |
| :-----------------: | :-----: |
| ToQUBO.jl           | v0.5.1  |
| QUBOTools.jl        | v0.15.1 |
| PyQUBO              | v1.5.0  |
| OpenQAOA            | excluded on Python 3.12 |
| qubovert            | v1.2.5  |
| Qiskit              | v2.4.1  |
| qiskit-optimization | v0.7.0  |
| docplex             | v2.32.264 |
| amplify             | v1.6.1  |
| dimod               | v0.12.22 |

The latest OpenQAOA release found on PyPI was `0.2.6`, but it does not resolve
for the Python 3.12 runtime used by the modern benchmark run. The historical
OpenQAOA results remain available in `archive/paper-v1`.

The live ToQUBO result CSVs also include `compiler_time` for the `optimize!`
step and `convert_time` for QUBOTools backend extraction. The `toqubo_time`
column remains their sum for compatibility with the existing plots.

## Instructions

First clone the repository

```shell
$ git clone https://github.com/JuliaQUBO/ToQUBO-benchmark.git
...
```

To run the code and plot the results

```shell
$ cd ./ToQUBO-benchmark
...

$ make
```

You can also do this separately

```shell
$ cd ./ToQUBO-benchmark
...

$ make install
...

$ make run
...

$ make report
...

$ make plot
...

```
