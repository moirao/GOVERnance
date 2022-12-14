
import taichi as ti
import numpy as np


@ti.func
def cross2d(a, b):
    return a[0] * b[1] - a[1] * b[0]


@ti.func
def inside_ccw(p, a, b, c):
    return cross2d(a - p, b - p) >= 0 and cross2d(
        b - p, c - p) >= 0 and cross2d(c - p, a - p) >= 0


@ti.data_oriented
class Voxelizer:
    def __init__(self, res, dx, super_sample=2, precision=ti.f64, padding=3):
        assert len(res) == 3
        res = list(res)
        for i in range(len(res)):
            r = 1
            while r < res[i]:
                r = r * 2
            res[i] = r
        print(f'Voxelizer resolution {res}')
        # Super sample by 2x
        self.res = (res[0] * super_sample, res[1] * super_sample,
                    res[2] * super_sample)
        self.dx = dx / super_sample
        self.inv_dx = 1 / self.dx
        self.voxels = ti.field(ti.i32)
        self.block = ti.root.pointer(
            ti.ijk, (self.res[0] // 8, self.res[1] // 8, self.res[2] // 8))
        self.block.dense(ti.ijk, 8).place(self.voxels)

        assert precision in [ti.f32, ti.f64]
        self.precision = precision
        self.padding = padding

    @ti.func
    def fill(self, p, q, height, inc):
        for i in range(self.padding, height):
            self.voxels[p, q, i] += inc

    @ti.kernel
    def voxelize_triangles(self, num_triangles: ti.i32,
                           triangles: ti.types.ndarray()):
        for i in range(num_triangles):
            jitter_scale = ti.cast(0, self.precision)
            if ti.static(self.precision == ti.f32):
                jitter_scale = 1e-4