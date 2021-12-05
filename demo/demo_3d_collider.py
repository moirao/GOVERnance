import taichi as ti
import numpy as np
import os
import utils
from engine.mpm_solver import MPMSolver

write_to_disk = False

if write_to_disk:
    os.makedirs('outputs', exist_ok=True)

# Try to run on GPU
ti.init(arch=ti.cuda, device_memory_GB=4.0)

gui = ti.GUI("Taichi Elements", res=512, background_color=0x112F41)

mpm = MPMSolver(res=(64, 64, 64), size=1)

mpm.set_gravity((0, -20, 0))

mpm.add_sphere_collider(center=(0.25, 0.5, 0.5),
                        radius=0.1,
                        surface=mpm.surface_slip)
mpm.add_sphere_collider(center=(0.5, 0.5, 0.5),
                        radius=