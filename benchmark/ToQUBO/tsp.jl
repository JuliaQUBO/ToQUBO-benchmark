using CSV
using JuMP
using ToQUBO
using Anneal

function tsp(n::Int)
    t₀ = @timed begin
        model = Model(() -> ToQUBO.Optimizer(ExactSampler.Optimizer))

        @variable(model, x[1:n, 1:n], Bin, Symmetric)

        @constraint(model, [i in 1:n], sum(x[i,:]) == 1)
        @constraint(model, [j in 1:n], sum(x[:,j]) == 1)

        D = fill(10, (n,n))

        @objective(model, Min, sum([D[i,j] * x[i,k] * x[j, (k % n)+1] for i = 1:n , j = 1:n, k = 1:n]))
    end

    t₁ = @timed begin
        qubo_model = ToQUBO.toqubo(JuMP.backend(model).model_cache)
        Q, α, β = ToQUBO.qubo(qubo_model)
    end

    return t₀.time, t₁.time
end


function measure(initial_size::Int, max_size::Int, step::Int)
    results = Dict{Int,Float64}()
    # tsp(2) # avoid time-to-first-solve
    for n in initial_size:step:max_size
        println("Variables: $(n*n)")
        t₀, t₁ = tsp(n)
        results[n*n] = t₀ + t₁  
        println("Model: $(t₀)")
        println("Convert to QUBO: $(t₁)")
        println("Total elapsed time: $(t₀ + t₁)")
        println("----------")
    end
    csv_path = joinpath(@__DIR__, "tsp_ToQUBO.csv")
    CSV.write(csv_path, sort(collect(results)), header = ["n_var","time"])
end

measure(5,100,5)