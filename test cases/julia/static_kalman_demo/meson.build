# Start of file
project('julia static kalman demo', 'c')

# Import the module we added
julia_mod = import('julia')
juliac = julia_mod.find_juliac()

# Build Julia library (adjust kind to 'shared' if preferred)
julialib = julia_mod.compile_library('kalman', 'kalman.jl', kind: 'static', juliac: juliac)

# Link to C executable
exe = executable('prog', 'main.c', link_with: [julialib])

test('run', exe)
# End of file
