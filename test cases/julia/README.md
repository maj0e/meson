# Start of file
JuliaC Meson module demo

This demo shows how to use mesonbuild/modules/julia.py to compile a Julia
source to a static library (using juliac) and link it to a C program.

Prereqs:
- Meson tree with the julia module placed under mesonbuild/modules/julia.py
- Julia >= 1.12 and the JuliaC.jl package installed, providing a `juliac` executable on PATH.

Quick steps:
  git checkout -b modules/julia
  cp mesonbuild/modules/julia.py <meson-tree>/mesonbuild/modules/
  cd "test cases/julia/static_kalman_demo"
  meson setup builddir
  meson compile -C builddir
  ./builddir/prog   # should print output from the Julia function

Notes:
- JuliaC CLI flags or symbol export rules may differ between JuliaC versions.
  You can pass extra arguments to juliac via the juliac_args kwarg to compile_library.
- On Windows, additional adjustments may be required for dll/import-lib names.
# End of file
