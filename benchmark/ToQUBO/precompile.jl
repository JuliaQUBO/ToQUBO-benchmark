using CSV
using JuMP
using ToQUBO
using Anneal


t₀ = @timed begin
    model = Model(() -> ToQUBO.Optimizer(ExactSampler.Optimizer))

    @variable(model, x[1:2, 1:2], Bin, Symmetric)

    @constraint(model, [i in 1:2], sum(x[i,1:2]) == 2)
    @constraint(model, [i in 1:2], sum(x[i,i]) == 0)

    D = fill(10, (2,2))

    @objective(model, Min, sum(D .* x)/2)

end

t₁ = @timed begin
    qubo_model = ToQUBO.toqubo(JuMP.backend(model).model_cache)
    Q, α, β = ToQUBO.qubo(qubo_model)
end

return t₀.time, t₁.time
