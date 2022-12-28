import taichi as ti
import numpy as np
import utils
from engine import mpm_solver

# Try to run on GPU
ti.init(arch=ti.cuda)

mpm = mpm_solver.MPMSolver(res=