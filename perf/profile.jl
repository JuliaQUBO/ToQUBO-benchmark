using Revise
using CSV
using JuMP
using ToQUBO
using Profile
using PProf

include("../benchmark/ToQUBO/problems.jl")

let n = 2
    _ = npp(n, npp_data(n))
end

let n = 1000
    @pprof npp(n, npp_data(n))
end

# # Save a graph that looks like the Jupyter example above
# ProfileSVG.save(joinpath(@__DIR__, "prof.svg"))

# ProfileVega.view() |> save("prof.svg")