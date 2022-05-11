
from engine.mesh_io import write_point_cloud
import numpy as np
import taichi as ti
import time
import gc


class ParticleIO:
    v_bits = 8
    x_bits = 32 - v_bits