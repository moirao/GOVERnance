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
f.write(requests.get(url).con