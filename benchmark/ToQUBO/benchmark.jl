using CSV
using JuMP
using ToQUBO
using LinearAlgebra
using Printf
using Statistics

include("problems.jl")

const SUMMARY_STATISTICS = ("min", "median", "mean", "std")

function env_int(name::String, default::Int, minimum::Int)
    value = get(ENV, name, string(default))
    parsed = tryparse(Int, value)

    if parsed === nothing
        error("$(name) must be an integer, got $(repr(value))")
    end
    if parsed < minimum
        error("$(name) must be at least $(minimum), got $(parsed)")
    end

    return parsed
end

function env_time_statistic()
    statistic = lowercase(strip(get(ENV, "BENCHMARK_TIME_STATISTIC", "min")))

    if !(statistic in ("min", "median", "mean"))
        error("BENCHMARK_TIME_STATISTIC must be one of: min, median, mean")
    end

    return statistic
end

function stats(values::Vector{Float64})
    return Dict(
        "min" => minimum(values),
        "median" => median(values),
        "mean" => mean(values),
        "std" => length(values) <= 1 ? 0.0 : std(values; corrected=false),
    )
end

function summarize_samples(samples; sample_count::Integer, warmup_count::Integer, statistic::String)
    summary = Dict{String,Float64}()

    for sample in samples
        sample["toqubo_time"] = sample["compiler_time"] + sample["convert_time"]
    end

    for key in ("model_time", "toqubo_time", "compiler_time", "convert_time", "total_time")
        values = [sample[key] for sample in samples]
        key_stats = stats(values)

        summary[key] = key_stats[statistic]

        for stat in SUMMARY_STATISTICS
            summary["$(key)_$(stat)"] = key_stats[stat]
        end
    end

    summary["time"] = summary["total_time"]

    for stat in SUMMARY_STATISTICS
        summary["time_$(stat)"] = summary["total_time_$(stat)"]
    end

    summary["sample_count"] = Float64(sample_count)
    summary["warmup_count"] = Float64(warmup_count)

    return summary
end

function benchmark(;
    key::String,
    path::AbstractString,
    run::Function,
    data::Function,
    nvar::Function,
    start::Integer,
    step::Integer,
    stop::Integer,
    sample_count::Integer=env_int("BENCHMARK_SAMPLES", 1, 1),
    warmup_count::Integer=env_int("BENCHMARK_WARMUPS", 1, 0),
    statistic::String=env_time_statistic(),
)
    results = []

    println("Problem: $(key)")

    # Keep Julia time-to-first-solve out of the first measured size.
    _ = run(3, data(3); skip_gc=true)

    for n in start:step:stop
        input_data = data(n)

        for _ in 1:warmup_count
            _ = run(n, input_data; skip_gc=true)
        end

        samples = [
            run(n, input_data; skip_gc=true)
            for _ in 1:sample_count
        ]
        time_info = summarize_samples(
            samples;
            sample_count=sample_count,
            warmup_count=warmup_count,
            statistic=statistic,
        )

        @printf(
            """
            -----------------------------
            Variables: %d (input: %d)
            Samples.............. %7d
            Warmups.............. %7d
            Model................ %7.3f
            Compilation.......... %7.3f
            Conversion........... %7.3f
            Total elapsed time... %7.3f
            """,
            nvar(n),
            n,
            sample_count,
            warmup_count,
            time_info["model_time"],
            time_info["compiler_time"],
            time_info["convert_time"],
            time_info["total_time"],
        )

        push!(
            results,
            (
                nvar = nvar(n),
                time = time_info["time"],
                jump_time = time_info["model_time"],
                toqubo_time = time_info["toqubo_time"],
                compiler_time = time_info["compiler_time"],
                convert_time = time_info["convert_time"],
                time_min = time_info["time_min"],
                time_median = time_info["time_median"],
                time_mean = time_info["time_mean"],
                time_std = time_info["time_std"],
                jump_time_min = time_info["model_time_min"],
                jump_time_median = time_info["model_time_median"],
                jump_time_mean = time_info["model_time_mean"],
                jump_time_std = time_info["model_time_std"],
                toqubo_time_min = time_info["toqubo_time_min"],
                toqubo_time_median = time_info["toqubo_time_median"],
                toqubo_time_mean = time_info["toqubo_time_mean"],
                toqubo_time_std = time_info["toqubo_time_std"],
                compiler_time_min = time_info["compiler_time_min"],
                compiler_time_median = time_info["compiler_time_median"],
                compiler_time_mean = time_info["compiler_time_mean"],
                compiler_time_std = time_info["compiler_time_std"],
                convert_time_min = time_info["convert_time_min"],
                convert_time_median = time_info["convert_time_median"],
                convert_time_mean = time_info["convert_time_mean"],
                convert_time_std = time_info["convert_time_std"],
                sample_count = sample_count,
                warmup_count = warmup_count,
            )
        )
    end

    csv_path = joinpath(path, "results.$(key).csv")
    CSV.write(
        csv_path,
        sort(collect(results)),
    )

    return nothing
end

# Travelling Salesperson
benchmark(; tsp_info...)

# Number Partitioning
benchmark(; npp_info...)

# Graph Coloring
# benchmark("gcp"; gcp_info...)
