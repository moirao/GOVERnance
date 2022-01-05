from plyfile import PlyData
import numpy as np


def load_mesh(fn, scale=1, offset=(0, 0, 0)):
    if isinstance(scale, (int, float)):
        scale = (scale, scale, scale)