using CSV
using JuMP
using ToQUBO
using Anneal
using Profile
using PProf

function tsp(n::Int)
    model = Model(ToQUBO.Optimizer)

    @variable(model, x[1:n, 1:n], Bin, Symmetric)

    @constraint(model, [i in 1:n], sum(x[i,:]) == 1)
    @constraint(model, [j in 1:n], sum(x[:,j]) == 1)

    D = fill(10, (n,n))

    @objective(model, Min, sum([D[i,j] * x[i,k] * x[j, (k % n)+1] for i = 1:n , j = 1:n, k = 1:n]))

    optimize!(model)
    
    Q, α, β = ToQUBO.qubo(model)
    
    return nothing
end

Profile.clear()
@pprof tsp(75)

# # Save a graph that looks like the Jupyter example above
# ProfileSVG.save(joinpath(@__DIR__, "prof.svg"))

# ProfileVega.view() |> save("prof.svg")