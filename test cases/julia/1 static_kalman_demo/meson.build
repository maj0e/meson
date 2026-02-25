project('static_kalman_demo', 'c')

juliac = find_program('juliac-wrapper')

lib = custom_target('kalman',
    input: 'kalman.jl',
    output: 'kalman.so',
    command: [juliac, '--output-lib', '@OUTPUT@', '@INPUT@'])

executable(
    'static_kalman_demo',
    'main.c',
    link_with: lib,
)
