"""
    Travelling Salesperson Problem
"""
function tsp_data(n::Integer)
    return Float64[10.0 * abs(i - j) for i = 1:n, j = 1:n]
end

function tsp(n::Int, D::Matrix{Float64}; skip_gc::Bool=false)
    skip_gc && GC.gc()

    tₜ = @timed begin
        # Build Model
        t₀ = @timed begin
            model = Model(ToQUBO.Optimizer)

            @variable(model, x[1:n, 1:n], Bin)

            @constraint(model, [i = 1:n], sum(x[i, :]) == 1)
            @constraint(model, [k = 1:n], sum(x[:, k]) == 1)

            @objective(model, Min, sum(x[:, k]' * D * x[:, k%n+1] for k = 1:n))
        end

        # Compile Model
        t₁ = @timed optimize!(model)

        # Convert to QUBO
        t₂ = @timed Q, α, β = ToQUBO.qubo(model, Dict)
    end

    return Dict{String,Float64}(
        "model_time"    => t₀.time,
        "compiler_time" => t₁.time,
        "convert_time"  => t₂.time,
        "total_time"    => tₜ.time,
    )
end

function tsp_nvar(n::Integer)
    return n * n
end

const tsp_info = Dict{Symbol,Any}(
    :key   => "tsp",
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

function npp(n::Int, s::Vector{Int}; skip_gc::Bool=false)
    skip_gc && GC.gc()

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
        t₂ = @timed Q, α, β = ToQUBO.qubo(model, Dict)
    end

    return Dict{String,Float64}(
        "model_time"    => t₀.time,
        "compiler_time" => t₁.time,
        "convert_time"  => t₂.time,
        "total_time"    => tₜ.time,
    )
end

function npp_nvar(n::Integer)
    return n
end

const npp_info = Dict{Symbol,Any}(
    :key   => "npp",
    :path  => @__DIR__,
    :run   => npp,
    :data  => npp_data,
    :nvar  => npp_nvar,
    :start => 20,
    :step  => 20,
    :stop  => 1_000,
)

# function gcp(n::Int, A::Matrix{Float64}; skip_gc::Bool=false)
#     skip_gc && GC.gc()

#     tₜ = @timed begin
#         # Build Model
#         t₀ = @timed begin
#             model = Model(ToQUBO.Optimizer)

#             @variable(model, x[1:n, 1:n], Bin)
#             @variable(model, c[1:n], Bin)

#             @constraint(model, [i = 1:n, k = 1:n], c[k] >= x[i, k])
#             @constraint(model, [i = 1:n, j = 1:n, k = 1:n], x[i,k] + x[j,k] <= A[i,j])
#             @constraint(model, [i = 1:n], sum(x[i,:]) == 1)

#             @objective(model, Min, sum(c))
#         end

#         # Compile Model
#         t₁ = @timed optimize!(model)

#         # Convert to QUBO
#         t₂ = @timed Q, α, β = ToQUBO.qubo(model, Dict)
#     end

#     return Dict{String,Float64}(
#         "model_time" => t₀.time,
#         "compiler_time" => t₁.time,
#         "convert_time" => t₂.time,
#         "total_time" => tₜ.time,
#     )
# end

# function gcp_nvar(n::Integer)
#     return n * n + n
# end

# const gcp_info = Dict{Symbol,Any}(
#     :path => @__DIR__,
#     :run => gcp,
#     :data => gcp_data,
#     :nvar => gcp_nvar,
#     :start => 5,
#     :step  => 5,
#     :stop  => 100,
# )