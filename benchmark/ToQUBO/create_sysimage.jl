using Pkg; Pkg.instantiate()
using PackageCompiler, Libdl

PackageCompiler.create_sysimage(
    ["JuMP", "ToQUBO"],
    sysimage_path = joinpath(@__DIR__, "sysimage.$(Libdl.dlext)"),
)
