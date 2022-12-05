using CSV
using JuMP
using ToQUBO
using Anneal

t₀ = @timed begin
    n = 3

    model = Model(ToQUBO.Optimizer)

    @variable(model, x[1:n, 1:n], Bin, Symmetric)

    @constraint(model, [i in 1:n], sum(x[i,:]) == 1)
    @constraint(model, [j in 1:n], sum(x[:,j]) == 1)

    D = fill(10, (n,n))

    @objective(model, Min, sum([D[i,j] * x[i,k] * x[j, (k % n)+1] for i = 1:n , j = 1:n, k = 1:n]))

    optimize!(model)
end

t₁ = @timed begin
    qubo_model = ToQUBO.toqubo(JuMP.backend(model).model_cache)
    Q, α, β    = ToQUBO.qubo(qubo_model)
end

return t₀.time, t₁.time
