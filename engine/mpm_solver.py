import taichi as ti
import numpy as np
import time
import numbers
import math
import multiprocessing as mp

USE_IN_BLENDER = False


# TODO: water needs Jp - fix this.


@ti.data_oriented
class MPMSolver:
    material_water = 0
    material_elastic = 1
    material_snow = 2
    material_sand = 3
    material_stationary = 4
    materials = {
        'WATER': material_water,
        'ELASTIC': material_elastic,
        'SNOW': material_snow,
        'SAND': material_sand,
        'STATIONARY': material_stationary,
    }

    # Surface boundary conditions

    # Stick to the boundary
    surface_sticky = 0
    # Slippy boundary
    surface_slip = 1
    # Slippy and free to separate
    surface_separate = 2

    surfaces = {
        'STICKY': surface_sticky,
        'SLIP': surface_slip,
        'SEPARATE': surface_separate
    }

    def __init__(
            self,
            res,
            quant=False,
            use_voxelizer=True,
            size=1,
            max_num_particles=2**30,
            # Max 1 G particles
            padding=3,
            unbounded=False,
            dt_scale=1,
            E_scale=1,
            voxelizer_super_sample=2,
            use_g2p2g=False,  # Ref: A massively parallel and scalable multi-GPU material point method
            v_clamp_g2p2g=True,
            use_bls=True,
            g2p2g_allowed_cfl=0.9,  # 0.0 for no CFL limit
            water_density=1.0,
            support_plasticity=True,  # Support snow and sand materials
            use_adaptive_dt=False,
            use_ggui=False,
            use_emitter_id=False
    ):
        self.dim = len(res)
        self.quant = quant
        self.use_g2p2g = use_g2p2g
        self.v_clamp_g2p2g = v_clamp_g2p2g
        self.use_bls = use_bls
        self.g2p2g_allowed_cfl = g2p2g_allowed_cfl
        self.water_density = water_density
        se