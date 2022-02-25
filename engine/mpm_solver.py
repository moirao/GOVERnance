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
                                                    (1 - 2 * self.nu))

        # Sand parameters
        friction_angle = math.radians(45)
        sin_phi = math.sin(friction_angle)
        self.alpha = math.sqrt(2 / 3) * 2 * sin_phi / (3 - sin_phi)

        # An empirically optimal chunk size is 1/10 of the expected particle number
        chunk_size = 2**20 if self.dim == 2 else 2**23
        self.particle = ti.root.dynamic(ti.i, max_num_particles, chunk_size)

        if self.quant:
            if not self.use_g2p2g:
                self.particle.place(self.C)
            if self.support_plasticity:
                self.particle.place(self.Jp)
            bitpack = ti.BitpackedFields(max_num_bits=64)
            bitpack.place(self.x)
            self.particle.place(bitpack)
            bitpack = ti.BitpackedFields(max_num_bits=64)
            bitpack.place(self.v, shared_exponent=True)
            self.particle.place(bitpack)

            if self.dim == 3:
                bitpack = ti.BitpackedFields(max_num_bits=32)
                bitpack.place(self.F.get_scalar_field(0, 0),
                              self.F.get_scalar_field(0, 1))
                self.particle.place(bitpack)
                bitpack = ti.BitpackedFields(max_num_bits=32)
                bitpack.place(self.F.get_scalar_field(0, 2),
                              self.F.get_scalar_field(1, 0))
                self.particle.place(bitpack)
                bitpack = ti.BitpackedFields(max_num_bits=32)
                bitpack.place(self.F.get_scalar_field(1, 1),
                              self.F.get_scalar_field(1, 2))
                self.particle.place(bitpack)
                bitpack = ti.BitpackedFields(max_num_bits=32)
                bitpack.place(self.F.get_scalar_field(2, 0),
                              self.F.get_scalar_field(2, 1))
                self.particle.place(bitpack)
                bitpack = ti.BitpackedFields(max_num_bits=32)
                bitpack.place(self.F.get_scalar_field(2, 2), self.material)
                self.particle.place(bitpack)
            else:
                assert self.dim == 2
                bitpack = ti.BitpackedFields(max_num_bits=32)
                bitpack.place(self.F.get_scalar_field(0, 0),
                              self.F.get_scalar_field(0, 1))
                self.particle.place(bitpack)
                bitpack = ti.BitpackedFields(max_num_bits=32)
                bitpack.place(self.F.get_scalar_field(1, 0),
                              self.F.get_scalar_field(1, 1))
                self.particle.place(bitpack)
                # No quantization on particle material in 2D
                self.particle.place(self.material)
            self.particle.place(self.color)
            if self.use_emitter_id:
                self.particle.place(self.emitter_ids)
        else:
            if self.use_emitter_id:
                self.particle.place(self.x, self.v, self.F, self.material,
                                self.color, self.emitter_ids)
            else:
                self.particle.place(self.x, self.v, self.F, self.material,
                                self.color)
            if self.support_plasticity:
                self.particle.place(self.Jp)
            if not self.use_g2p2g:
                self.particle.place(self.C)

        if self.use_ggui:
            self.particle.place(self.color_with_alpha)

        self.total_substeps = 0
        self.unbounded = unbounded

        if self.dim == 2:
            self.voxelizer = None
            self.set_gravity((0, -9.8))
        else:
            if use_voxelizer:
                if USE_IN_BLENDER:
                    from .voxelizer import Voxelizer
                else:
                    from engine.voxelizer import Voxelizer
                self.voxelizer = Voxelizer(res=self.res,
                                           dx=self.dx,
                                           padding=self.padding,
                                           super_sample=voxelizer_super_sample)
            else:
                self.voxelizer = None
            self.set_gravity((0, -9.8, 0))

        self.voxelizer_super_sample = voxelizer_super_sample

        self.grid_postprocess = []

        self.add_bounding_box(self.unbounded)

        self.writers = []

        if not self.use_g2p2g:
            self.grid = self.grid[0]
            self.grid_v = self.grid_v[0]
            self.grid_m = self.grid_m[0]
            self.pid = self.pid[0]

    @ti.func
    def stencil_range(self):
        return ti.ndrange(*((3, ) * self.dim))

    def set_gravity(self, g):
        assert isinstance(g, (tuple, list))
        assert len(g) == self.dim
        self.gravity[None] = g

    @ti.func
    def sand_projection(self, sigma, p):
        sigma_out = ti.Matrix.zero(ti.f32, self.dim, self.dim)
        epsilon = ti.Vector.zero(ti.f32, self.dim)
        for i in ti.static(range(self.dim)):
            epsilon[i] = ti.log(max(abs(sigma[i, i]), 1e-4))
            sigma_out[i, i] = 1
        tr = epsilon.sum() + self.Jp[p]
        epsilon_hat = epsilon - tr / self.dim
        epsilon_hat_norm = epsilon_hat.norm() + 1e-20
        if tr >= 0.0:
            self.Jp[p] = tr
        else:
            self.Jp[p] = 0.0
            delta_gamma = epsilon_hat_norm + (
                self.dim * self.lambda_0 +
                2 * self.mu_0) / (2 * self.mu_0) * tr * self.alpha
            for i in ti.static(range(self.dim)):
                sigma_out[i, i] = ti.exp(epsilon[i] - max(0, delta_gamma) /
                                         epsilon_hat_norm * epsilon_hat[i])

        return sigma_out

    @ti.kernel
    def build_pid(self, pid: ti.template(), grid_m: ti.template(),
                  offset: ti.template()):
        """
        grid has blocking (e.g. 4x4x4), we wish to put the particles from each block into a GPU block,
        then used shared memory (ti.block_local) to accelerate
        :param pid:
        :param grid_m:
        :param offset:
        :return:
        """
        ti.loop_config(block_dim=64)
        for p in self.x:
            base = int(ti.floor(self.x[p] * self.inv_dx - 0.5)) \
                   - ti.Vector(self.offset)
            # Pid grandparent is `block`
            base_pid = ti.rescale_index(grid_m, pid.parent(2), base)
            ti.append(pid.parent(), base_pid, p)

    @ti.kernel
    def g2p2g(self, dt: ti.f32, pid: ti.template(), grid_v_in: ti.template(),
              grid_v_out: ti.template(), grid_m_out: ti.template()):
        ti.loop_config(block_dim=256)
        ti.no_activate(self.particle)
        if ti.static(self.use_bls):
            ti.block_local(grid_m_out)
            for d in ti.static(range(self.dim)):
                ti.block_local(grid_v_in.get_scalar_field(d))
                ti.block_local(grid_v_out.get_scalar_field(d))
        for I in ti.grouped(pid):
            p = pid[I]
            # G2P
            base = ti.floor(self.x[p] * self.inv_dx - 0.5).cast(int)
            Im = ti.rescale_index(pid, grid_m_out, I)
            for D in ti.static(range(self.dim)):
                base[D] = ti.assume_in_range(base[D], Im[D], 0, 1)
            fx = self.x[p] * self.inv_dx - base.cast(float)
            w = [
                0.5 * (1.5 - fx)**2, 0.75 - (fx - 1.0)**2, 0.5 * (fx - 0.5)**2
            ]
            new_v = ti.Vector.zero(ti.f32, self.dim)
            C = ti.Matrix.zero(ti.f32, self.dim, self.dim)
            # Loop over 3x3 grid node neighborhood
            for offset in ti.static(ti.grouped(self.stencil_range())):
                dpos = offset.cast(float) - fx
                g_v = grid_v_in[base + offset]
                weight = 1.0
                for d in ti.static(range(self.dim)):
                    weight *= w[offset[d]][d]
                new_v += weight * g_v
                C += 4 * self.inv_dx * weight * g_v.outer_product(dpos)

            if p >= self.last_time_final_particles[None]:
                # New particles. No G2P.
                new_v = self.v[p]
                C = ti.Matrix.zero(ti.f32, self.dim, self.dim)

            if self.material[p] != self.material_stationary:
                self.v[p] = new_v
                self.x[p] += dt * self.v[p]  # advection

            # P2G
            base = ti.floor(self.x[p] * self.inv_dx - 0.5).cast(int)
            for D in ti.static(range(self.dim)):
                base[D] = ti.assume_in_range(base[D], Im[D], -1, 2)

            fx = self.x[p] * self.inv_dx - float(base)
            # Quadratic kernels  [http://mpm.graphics   Eqn. 123, with x=fx, fx-1,fx-2]
            w2 = [0.5 * (1.5 - fx)**2, 0.75 - (fx - 1)**2, 0.5 * (fx - 0.5)**2]
            # Deformation gradient update
            new_F = (ti.Matrix.identity(ti.f32, self.dim) + dt * C) @ self.F[p]
            if ti.static(self.quant):
                new_F = max(-self.F_bound, min(self.F_bound, new_F))
            self.F[p] = new_F
            # Hardening coefficient: snow gets 