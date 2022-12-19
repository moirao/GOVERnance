import taichi as ti
import utils
import math
from engine import mpm_solver

ti.init(arch=ti.cuda,
        device_memory_GB=1.0)  # Try to run on GPU
mpm = mpm_solver.MPMSolver(res=(24, 24))

for frame in range(5):
    mpm.step(8e-3)
    mpm.add_cube(lower_corner=[0.3, 0.7],
  