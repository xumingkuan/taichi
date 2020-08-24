import taichi as ti

from async_cases import *

rerun = True

cases = [
    fuse_dense_x2y2z,
    fuse_reduction,
    fill_1d,
    fill_scalar,
    sparse_numpy,
    stencil_reduction,
]

if rerun:
    for c in cases:
        c()

case_names = [c.__name__ for c in cases]

ti.benchmark_plot(fn='benchmark.yml',
                  cases=case_names,
                  archs=['x64'],
                  bars='async_regression',
                  left_margin=0.2)
