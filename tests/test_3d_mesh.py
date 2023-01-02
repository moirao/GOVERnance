import taichi as ti
import numpy as np
import utils
import requests
import zipfile
import os
from engine import mpm_solver

folder = 'tests'
zip_file_path = os.path.join(folder, 'suzanne_npy.zip')
f = open(zip_file_path, 'wb')
url = 'https://github.com/taichi-dev/taichi_elements_blender_examples/releases/download/suzanne_npy/suzanne_npy.zip'
f.write(requests.get(url).content)
f.close()

z = zipfile.ZipFile(zip_file_path, 'r')
z.extractall(path='tests' + os.sep)
z.close()

# Try to run on GPU
ti.init(arch=ti.cuda)

mpm = mpm_solver.MPMSolver(res=(24, 24, 24), size=1)

triangles = np.fromfile(os.path.join(folder, 'suzanne.npy'), dtype=np.float32)
triangles = np.reshape(triangles, (len(triangles) // 9, 9)) * 0.306 + 0.501

os.remove(zip_file_path)
os.remove(os.path.join(folder, 'suzanne.npy'))

mpm.add_mesh(triangles=triangles,
             material=mpm_solver.MPMSolver.mate