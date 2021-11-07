import taichi as ti
import numpy as np
import utils
from engine.mpm_solver import MPMSolver

write_to_disk = False

# Try to run on GPU
ti.init(arch=ti.cuda, kernel_profiler=True)

gui = ti.GUI("MPM Benchmark", res=256, background_color=0x1