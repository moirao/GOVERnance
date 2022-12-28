import taichi as ti
import numpy as np
import utils
from engine import mpm_solver

# Try to run on GPU
ti.init(arch=ti.cuda)

mpm = mpm_solver.MPMSolver(res=(24, 24, 24), size=1)
mpm.set_gravity((0, -20, 0))

mpm.add_sphere_collider(center=(0.25, 0.5, 0.5),
                        radius=0.1,
                        surface=mpm.surface_slip)
mpm.add_sphere_collider(center=(0.5, 0.5, 0.5),
                        radius=0.1,
                        surface=mpm.surface_sticky)
mpm.add_sphere_collider(center=(0.75, 0.5, 0.5),
        