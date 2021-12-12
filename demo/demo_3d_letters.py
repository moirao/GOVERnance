import taichi as ti
import math
import time
import numpy as np
from plyfile import PlyData, PlyElement
import os
import utils
from utils import create_output_folder
from engine.mpm_solver import MPMSolver

with_gui = True
write_to_disk = True

# Try to run on GPU
ti.init(arch=ti.cuda, kernel_profiler=True, device_memory_fraction=0.7)

max_num_particles = 10000000

if with_gui:
    gui = ti.GUI("MLS-MPM", res=512, background_color=0x112F41)

if write_to_disk:
    output_dir = create_output_folder('./sim')


def load_mesh(fn, scale, offset):
    print(f'loading {fn}')
    plydata = PlyData.read(fn)
    x = plydata['vertex']['x']
    y = plydata['vertex']['y']
    z = plydata['vertex']['z']
    elements = plydata['face']
    num_tris = len(elements['vertex_indices'])
    triangles = np.zeros((num_tris, 9), dtype=np.float32)

    for i, face in enumerate(elements['vertex_indices']):
        assert len(face) == 3
        for d in range(3):
            triangles[i, d * 3 + 0] = x[face[d]] * scale + offset[0]
            triangles[i, d * 3 + 1] = y[face[d]] * scale + offset[1]
            triangles[i, d * 3 + 2] = z[face[d]] * scale + offset[2]

    print('loaded')

    return triangles


# Use 512 for final simulation/render
R = 256

mpm = MPMSolver(res=(R, R, R), size=1, unbounded=True, dt_scale=1)

mpm.add_surface_collider(point=(0, 0, 0),
                         normal=(0, 1, 0),
                         surface=mpm.surface_slip,
                         friction=0.5)

triangles = load_mesh('taichi.ply', scale=0.02, offset=(0.5, 0.6, 0.5))

mpm.set_gravity((0, -25, 0))


def visualize(particles):
    np_x = particles['position'] / 1.0

