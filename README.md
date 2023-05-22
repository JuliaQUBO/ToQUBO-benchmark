# ToQUBO-benchmark

Benchmarks for a paper on [QUBO.jl](https://github.com/psrenergy/QUBO.jl)

[![arXiv](https://img.shields.io/badge/arXiv-1234.56789-b31b1b.svg)]()


<div align="center">
    <img src="./data/results.png" alt="Benchmark Results" width="700px">
</div>

## How to reproduce the results
<center>
<table>
  <tr>
    <th colspan="2">Requirements</th>
  </tr>
  <tr>
    <td>OS</td>
    <td>Linux</td>
  </tr>
  <tr>
    <td>Python</td>
    <td>3.11</td>
  </tr>
  <tr>
    <td>Julia</td>
    <td>1.9</td>
  </tr>
</table>
</center>

First clone the repository

```shell
git clone https://github.com/psrenergy/ToQUBO-benchmark.git
```

To run the code and plot the results
```
cd ./ToQUBO-benchmark
make
```

You can also do this separately
```
cd ./ToQUBO-benchmark
make run
make plot
```
