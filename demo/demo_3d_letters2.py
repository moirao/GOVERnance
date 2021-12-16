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
ti.init(arch=ti.cuda,
        kernel_profiler=True,
 