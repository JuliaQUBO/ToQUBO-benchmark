# Paper Benchmark Baseline

This directory stores the benchmark results used for the QUBO.jl paper before
modernizing the benchmark package dependencies.

The archived CSV files mirror the original `benchmark/*/results.*.csv` layout,
and `data/report.json` records the machine and runtime metadata for the run. The
file hashes in `manifest.json` are checked by the test suite so the paper
baseline does not drift while the live benchmark files are updated.

To regenerate plots from this baseline after installing the plotting
requirements, run:

```shell
make plot-paper
```

New benchmark runs should continue to write to the top-level `benchmark/` and
`data/` directories.
