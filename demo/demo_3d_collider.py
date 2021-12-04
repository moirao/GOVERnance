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

gui