import taichi as ti
import numpy as np
import utils
import requests
import zipfile
import os
from engine import mpm_solver

folder = 'tests'
zip_file_path = os.path.join(folder, 'suzanne_npy.zip')
