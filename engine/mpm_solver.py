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
        self.grid_size = 4096

        assert self.dim in (
            2, 3), "MPM solver supports only 2D and 3D simulations."

        self.t = 0.0
        self.res = res
        self.n_particles = ti.field(ti.i32, shape=())
        self.dx = size / res[0]
        self.inv_dx = 1.0 / self.dx
        self.default_dt = 2e-2 * self.dx / size * dt_scale
        self.p_vol = self.dx**self.dim
        self.p_rho = 1000
        self.p_mass = self.p_vol * self.p_rho
        self.max_num_particles = max_num_particles
        self.gravity = ti.Vector