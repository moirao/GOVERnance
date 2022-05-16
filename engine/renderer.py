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

        self.camera_pos = ti.Vector.field(3, dtype=ti.f32, sha