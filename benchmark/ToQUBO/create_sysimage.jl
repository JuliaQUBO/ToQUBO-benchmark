using PackageCompiler, Libdl
PackageCompiler.create_sysimage(
    ["JuMP", "ToQUBO"],
    sysimage_path = joinpath(@__DIR__, "sysimage.$(Libdl.dlext)"),
    precompile_execution_file = [ joinpath(@__DIR__, "precompile.jl") ],
)
