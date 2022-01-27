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
        self.gravity = ti.Vector.field(self.dim, dtype=ti.f32, shape=())
        self.source_bound = ti.Vector.field(self.dim, dtype=ti.f32, shape=2)
        self.source_velocity = ti.Vector.field(self.dim,
                                               dtype=ti.f32,
                                               shape=())
        self.input_grid = 0
        self.all_time_max_velocity = 0
        self.support_plasticity = support_plasticity
        self.use_adaptive_dt = use_adaptive_dt
        self.use_ggui = use_ggui
        self.F_bound = 4.0

        # Affine velocity field
        if not self.use_g2p2g:
            self.C = ti.Matrix.field(self.dim, self.dim, dtype=ti.f32)
        # Deformation gradient

        if quant:
            qft = ti.types.quant.fixed(21, max_value=2.0)
            self.x = ti.Vector.field(self.dim, dtype=qft)

            qft = ti.types.quant.float(exp=7, frac=19)
            self.v = ti.Vector.field(self.dim, dtype=qft)

            qft = ti.types.quant.fixed(16, max_value=(self.F_bound + 0.1))
            self.F = ti.Matrix.field(self.dim, self.dim, dtype=qft)
        else:
            self.v = ti.Vector.field(self.dim, dtype=ti.f32)
            self.x = ti.Vector.field(self.dim, dtype=ti.f32)
            self.F = ti.Matrix.field(self.dim, self.dim, dtype=ti.f32)

        self.use_emitter_id = use_emitter_id
        if self.use_emitter_id:
            self.emitter_ids = ti.field(dtype=ti.i32)

        self.last_time_final_particles = ti.field(dtype=ti.i32, shape=())
        # Material id
        if quant and self.dim == 3:
            self.material = ti.field(dtype=ti.types.quant.int(16, False))
        else:
            self.material = ti.field(dtype=ti.i32)
        # Particle color
        self.color = ti.field(dtype=ti.i32)
        if self.use_ggui:
            self.color_with_alpha = ti.Vector.field(4, dtype=ti.f32)
        # Plastic deformation volume ratio
        if self.support_plasticity:
            self.Jp = ti.field(dtype=ti.f32)

        if self.dim == 2:
            indices = ti.ij
        else:
            indices = ti.ijk

        if unbounded:
            # The maximum grid size must be larger than twice of
            # simulation resolution in an unbounded simulation,
            # Otherwise the top and right sides will be bounded by grid size
            while self.grid_size <= 2 * max(self.res):
                self.grid_size *= 2  # keep it power of two
        offset = tuple(-self.grid_size // 2 for _ in range(self.dim))
        self.offset = offset

        self.num_grids = 2 if self.use_g2p2g else 1

        grid_block_size = 128
        if self.dim == 2:
            self.leaf_block_size = 16
        else:
            # TODO: use 8?
            self.leaf_block_size = 4

        self.grid = []
        self.grid_v = []
        self.grid_m = []
        self.pid = []

        for g in range(self.num_grids):
            # Grid node momentum/velocity
            grid_v = ti.Vector.field(self.dim, dtype=ti.f32)
            grid_m = ti.field(dtype=ti.f32)
            pid = ti.field(ti.i32)
            self.grid_v.append(grid_v)
            # Grid node mass
            self.grid_m.append(grid_m)
            grid = ti.root.pointer(indices, self.grid_size // grid_block_size)
            block = grid.pointer(indices,
                                 grid_block_size // self.leaf_block_size)
            self.block = block
            self.grid.append(grid)

            def block_component(c):
                block.dense(indices, self.leaf_block_size).place(c,
                                                                 offset=offset)

            block_component(grid_m)
            for d in range(self.dim):
                block_component(grid_v.get_scalar_field(d))

            self.pid.append(pid)

            block_offset = tuple(o // self.leaf_block_size
                                 for o in self.offset)
            self.block_offset = block_offset
            block.dynamic(ti.axes(self.dim),
                          1024 * 1024,
                          chunk_size=self.leaf_block_size**self.dim * 8).place(
                              pid, offset=block_offset + (0, ))

        self.padding = padding

        # Young's modulus and Poisson's ratio
        self.E, self.nu = 1e6 * size * E_scale, 0.2
        # Lame parameters
        self.mu_0, self.lambda_0 = self.E / (
            2 * (1 + self.nu)), self.E * self.nu / ((1 + self.nu) *
             