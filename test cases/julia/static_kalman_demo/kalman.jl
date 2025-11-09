# Start of file
# Minimal Julia file that exposes a C-callable function using @cfunction.
# The exact export name and mechanism may need adapting to your juliac toolchain.

function hello()::Cint
    return 42
end

# Expose a C-callable pointer. Some JuliaC toolchains can export a symbol for this.
# If your juliac expects different style (e.g. explicit exported wrapper), adapt accordingly.
const hello_from_julia = @cfunction(hello, Cint, ())
# End of file
