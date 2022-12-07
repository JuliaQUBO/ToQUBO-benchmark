using CSV
using JuMP
using ToQUBO

n     = 5
D     = fill(10, (n,n))
model = Model(ToQUBO.Optimizer)

@variable(model, x[1:n, 1:n], Bin, Symmetric)

@constraint(model, [i in 1:n], sum(x[i,:]) == 1)
@constraint(model, [j in 1:n], sum(x[:,j]) == 1)

@objective(model, Min, sum([D[i,j] * x[i,k] * x[j, (k % n)+1] for i = 1:n , j = 1:n, k = 1:n]))

optimize!(model)

Q, α, β = ToQUBO.qubo(unsafe_backend(model))