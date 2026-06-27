# Publication 10-Sample Benchmark Baseline

This directory stores the fixed modern benchmark refresh
`publication-10-sample-full-2026-06-25`.

The archived files mirror the live `benchmark/*/results.*.csv` result files and
the checked-in `data/` report and plot artifacts from the refresh. The manifest
records source commits, environment metadata, package versions, methodology,
ToQUBO extraction metadata, and SHA-256 hashes for the archived files.

This baseline used ten measured samples per problem size after one per-size
warmup. CSV `time` values store the minimum sample for compatibility with older
consumers; the archived PNG and PDF plots show the mean with 95% confidence
intervals and a dashed minimum trace.

New benchmark runs should continue to write to the top-level `benchmark/` and
`data/` directories.
