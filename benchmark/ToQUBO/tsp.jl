using CSV
using JuMP
using ToQUBO

function tsp(n::Int; clear_gc::Bool = false)
    clear_gc && GC.gc()

    # Problem Data
    D = fill(10, (n,n))

    # Build Model
    t₀ = @timed(begin
        model = Model(ToQUBO.Optimizer)

        @variable(model, x[1:n, 1:n], Bin, Symmetric)

        @constraint(model, [i in 1:n], sum(x[i,:]) == 1)
        @constraint(model, [j in 1:n], sum(x[:,j]) == 1)

        @objective(model, Min, sum(D[i,j] * x[i,k] * x[j, (k % n)+1] for i = 1:n , j = 1:n, k = 1:n))
    end).time

    clear_gc && GC.gc()

    # Compile Model
    t₁ = @timed(optimize!(model)).time

    # Convert to QUBO
    t₂ = @timed(Q, α, β = ToQUBO.qubo(unsafe_backend(model))).time

    return t₀, t₁, t₂
end

function main(initial_size::Int, max_size::Int, step::Int)
    results = []

    tsp(2) # avoid time-to-first-solve
    
    for n in initial_size:step:max_size
        t₀, t₁, t₂ = tsp(n; clear_gc=true)
        tₜ = t₀ + t₁ + t₂

        println(
            """
            -------------------------------------
            Variables: $(n * n)
            Model................ $(t₀)
            Compilation.......... $(t₁)
            Conversion........... $(t₂)
            Total elapsed time... $(tₜ)
            """
        )

        push!(results, (n * n, tₜ, t₀, t₁ + t₂))
    end

    csv_path = joinpath(@__DIR__, "results.csv")
    CSV.write(csv_path, sort(collect(results)), header = ["n_var","time","jump_time","toqubo_time"])
end

main(5,100,5)
