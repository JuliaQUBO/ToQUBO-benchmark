using CSV
using JuMP
using ToQUBO
using LinearAlgebra
using Printf

include("problems.jl")

function benchmark(;
    key::String,
    path::AbstractString,
    run::Function,
    data::Function,
    nvar::Function,
    start::Integer,
    step::Integer,
    stop::Integer
)
    results = []

    println("Problem: $(key)")

    # avoid time-to-first-solve
    _ = run(3, data(3))

    n = start
    while true
        time_info = run(n, data(n); skip_gc=true)

        @printf(
            """
            -----------------------------
            Variables: %d (input: %d)
            Model................ %7.3f
            Compilation.......... %7.3f
            Conversion........... %7.3f
            Total elapsed time... %7.3f
            """,
            nvar(n),
            n,
            time_info["model_time"],
            time_info["compiler_time"],
            time_info["convert_time"],
            time_info["total_time"],
        )
        if  key == "tsp" && time_info["total_time"] > 100.0
            break
        end
        if key == "npp" && time_info["total_time"] > 5.0
            break
        end
        push!(
            results,
            (
                nvar(n),
                time_info["total_time"],
                time_info["model_time"],
                time_info["compiler_time"] + time_info["convert_time"],
            )
        )
        n += step
    end

    csv_path = joinpath(path, "results.$(key).csv")
    CSV.write(csv_path, sort(collect(results)), header=["nvar", "time", "jump_time", "toqubo_time"])

    return nothing
end

# Travelling Salesperson
benchmark(; tsp_info...)

# Number Partitioning
benchmark(; npp_info...)

# Graph Coloring
# benchmark("gcp"; gcp_info...)