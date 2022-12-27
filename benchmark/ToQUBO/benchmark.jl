using CSV
using JuMP
using ToQUBO
using LinearAlgebra
using Printf

"""
    Travelling Salesperson Problem
"""
function tsp_data(n::Integer)
    return Float64[10.0 * abs(i - j) for i = 1:n, j = 1:n]
end

function tsp(n::Int, D::Matrix{Float64}; clear_gc::Bool=false)
    clear_gc && GC.gc()

    tₜ = @timed begin
        # Build Model
        t₀ = @timed begin
            model = Model(ToQUBO.Optimizer)

            @variable(model, x[1:n, 1:n], Bin, Symmetric)

            @constraint(model, [i = 1:n], sum(x[i, :]) == 1)
            @constraint(model, [k = 1:n], sum(x[:, k]) == 1)

            @objective(model, Min, sum(x[:, k]' * D * x[:, k%n+1] for k = 1:n))
        end

        # Compile Model
        t₁ = @timed optimize!(model)

        # Convert to QUBO
        t₂ = @timed Q, α, β = ToQUBO.qubo(unsafe_backend(model))
    end

    return Dict{String,Float64}(
        "model_time" => t₀.time,
        "compiler_time" => t₁.time,
        "convert_time" => t₂.time,
        "total_time" => tₜ.time,
    )
end

function tsp_nvar(n::Integer)
    return n * n
end

const tsp_info = Dict{Symbol,Any}(
    :path  => @__DIR__,
    :run   => tsp,
    :data  => tsp_data,
    :nvar  => tsp_nvar,
    :start => 5,
    :step  => 5,
    :stop  => 100,
)


"""
    Number Partitioning Problem
"""
function npp_data(n::Int)
    return collect(1:n)
end

function npp(n::Int, s::Vector{Int}; clear_gc::Bool=false)
    clear_gc && GC.gc()

    tₜ = @timed begin
        # Build Model
        t₀ = @timed begin
            model = Model(ToQUBO.Optimizer)

            @variable(model, x[1:n], Bin)

            # ‖∑ᵢ xᵢ sᵢ - ∑ᵢ x̄ᵢ sᵢ‖ = ‖∑ᵢ (xᵢ - x̄ᵢ) sᵢ‖
            #                       = ‖∑ᵢ (2xᵢ - 1) sᵢ‖
            #                       = ⟨2x - 1, s⟩²
            @objective(model, Min, ((2x .- 1)'s)^2)
        end

        # Compile Model
        t₁ = @timed optimize!(model)

        # Convert to QUBO
        t₂ = @timed Q, α, β = ToQUBO.qubo(unsafe_backend(model))
    end

    return Dict{String,Float64}(
        "model_time" => t₀.time,
        "compiler_time" => t₁.time,
        "convert_time" => t₂.time,
        "total_time" => tₜ.time,
    )
end

function npp_nvar(n::Integer)
    return n
end

const npp_info = Dict{Symbol,Any}(
    :path => @__DIR__,
    :run => npp,
    :data => npp_data,
    :nvar => npp_nvar,
    :start => 10,
    :step  => 20,
    :stop  => 1_000,
)

function benchmark(
    key::String;
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

    run(2, data(2)) # avoid time-to-first-solve

    for n in start:step:stop
        time_info = run(n, data(n); clear_gc=true)

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

        push!(
            results,
            (
                nvar(n),
                time_info["total_time"],
                time_info["model_time"],
                time_info["compiler_time"] + time_info["convert_time"],
            )
        )
    end

    csv_path = joinpath(path, "results.$(key).csv")
    CSV.write(csv_path, sort(collect(results)), header=["nvar", "time", "jump_time", "toqubo_time"])
end

benchmark("tsp"; tsp_info...)
benchmark("npp"; npp_info...)