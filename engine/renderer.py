import taichi as ti
import numpy as np
import math
import time
from engine.renderer_utils import out_dir, ray_aabb_intersection, inf, eps, \
  intersect_sphere, sphere_aabb_intersect_motion, inside_taichi

from engine.particle_io import ParticleIO

res = 1280, 720
aspect_ratio = res[0] / res[1]

max_ray_depth = 4
use_directional_light = True

dist_limit = 100
# TODO: why doesn't it render normally when shutter_begin = -1?
shutter_begin = -0.5

exposure = 1.5
light_direction = [1.2, 0.3, 0.7]
light_direction_noise = 0.03
light_color = [1.0, 1.0, 1.0]


@ti.data_oriented
class Renderer:
    def __init__(self,
                 dx=1 / 1024,
                 sphere_radius=0.3 / 1024,
                 render_voxel=False,
                 shutter_time=1e-3,
                 taichi_logo=True,
                 max_num_particles_million=128):
        self.vignette_strength = 0.9
        self.vignette_radius = 0.0
        self.vignette_center = [0.5, 0.5]
        self.taichi_logo = taichi_logo
        self.shutter_time = shutter_time  # usually half the frame time
        self.enable_motion_blur = self.shutter_time != 0.0

        self.color_buffer = ti.Vector.field(3, dtype=ti.f32)
        self.bbox = ti.Vector.field(3, dtype=ti.f32, shape=2)
        self.voxel_grid_density = ti.field(dtype=ti.f32)
        self.voxel_has_particle = ti.field(dtype=ti.i32)
        self.fov = ti.field(dtype=ti.f32, shape=())

        self.particle_x = ti.Vector.field(3, dtype=ti.f32)
        if self.enable_motion_blur:
            self.particle_v = ti.Vector.field(3, dtype=ti.f32)
        self.particle_color = ti.Vector.field(3, dtype=ti.u8)
        self.pid = ti.field(ti.i32)
        self.num_particles = ti.field(ti.i32, shape=())

        self.render_voxel = render_voxel

        self.voxel_edges = 0.1

        self.particle_grid_res = 2048

        self.dx = dx
        self.inv_dx = 1 / self.dx

        self.camera_pos = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.look_at = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.up = ti.Vector.field(3, dtype=ti.f32, shape=())

        self.floor_height = ti.field(dtype=ti.f32, shape=())

        self.supporter = 2
        self.sphere_radius = sphere_radius
        self.particle_grid_offset = [
            -self.particle_grid_res // 2 for _ in range(3)
        ]

        self.voxel_grid_res = self.particle_grid_res
        voxel_grid_offset = [-self.voxel_grid_res // 2 for _ in range(3)]
        self.max_num_particles_per_cell = 8192 * 1024
        self.max_num_particles = 1024 * 1024 * max_num_particles_million

        self.voxel_dx = self.dx
        self.voxel_inv_dx = 1 / self.voxel_dx

        assert self.sphere_radius * 2 < self.dx

        ti.root.dense(ti.ij, res).place(self.color_buffer)

        self.block_size = 8
        self.block_offset = [
            o // self.block_size for o in self.particle_grid_offset
        ]
        self.particle_bucket = ti.root.pointer(
            ti.ijk, self.particle_grid_res // self.block_size)

        self.particle_bucket.dense(ti.ijk, self.block_size).dynamic(
            ti.l, self.max_num_particles_per_cell,
            chunk_size=32).place(self.pid,
                                 offset=self.particle_grid_offset + [0])

        self.voxel_block_offset = [
            o // self.block_size for o in voxel_grid_offset
        ]
        ti.root.pointer(ti.ijk,
                        self.particle_grid_res // self.block_size).dense(
                            ti.ijk,
                            self.block_size).place(self.voxel_has_particle,
                                                   offset=voxel_grid_offset)
        voxel_block = ti.root.pointer(ti.ijk,
                                      self.voxel_grid_res // self.block_size)

        voxel_block.dense(ti.ijk,
                          self.block_size).place(self.voxel_grid_density,
                                                 offset=voxel_grid_offset)

        particle = ti.root.dense(ti.l, self.max_num_particles)

        particle.place(self.particle_x)
        if self.enable_motion_blur:
            particle.place(self.particle_v)
        particle.place(self.particle_color)

        self.set_up(0, 1, 0)
        self.set_fov(0.23)

    @ti.func
    def inside_grid(self, ipos):
        return ipos.min() >= -self.voxel_grid_res // 2 and ipos.max(
        ) < self.voxel_grid_res // 2

    # The dda algorithm requires the voxel grid to have one surrounding layer of void region
    # to correctly render the outmost voxel faces
    @ti.func
    def inside_grid_loose(self, ipos):
        return ipos.min() >= -self.voxel_grid_res // 2 - 1 and ipos.max(
        ) <= self.voxel_grid_res // 2

    @ti.func
    def query_density(self, ipos):
        inside = self.inside_grid(ipos)
        ret = 0.0
        if inside:
            ret = self.voxel_grid_density[ipos]
        else:
            ret = 0.0
        return ret

    @ti.func
    def voxel_color(self, pos):
        p = pos * self.inv_dx

        p -= t