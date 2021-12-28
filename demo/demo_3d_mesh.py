import taichi as ti
import numpy as np
import utils
from engine.mpm_solver import MPMSolver

write_to_disk = False

# Try to run on GPU
ti.init(arch=ti.cuda, device_memory_GB=3.0)

gui = ti.GUI("Taichi Elements", res=512, background_color=0x112F41)

mpm = MPMSolver(res=(64, 64, 64), size=1)

triangles = np.fromfile('suzanne.npy', dtype=np.float32)
triangles = np.reshape(triangles, (len(triangles) // 9, 9)) * 0.306 + 0.501

mpm.add_mesh(triangles=triangles,
             material=MPMSolver.material_elastic,
             color=0xFFFF