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

## How to reproduce the results

## Environment

| Linux  | Ubuntu 22.04 / 24.04 |
| :----: | :------------------: |
| Python | CPython 3.12         |
| Julia  | julia 1.12.6         |

## Packages

| Package             | Version |
| :-----------------: | :-----: |
| ToQUBO.jl           | v0.4.0  |
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

$ make plot
...

```
