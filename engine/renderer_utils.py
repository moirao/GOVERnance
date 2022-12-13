
import taichi as ti
import math

eps = 1e-4
inf = 1e10


@ti.func
def out_dir(n):
    u = ti.Vector([1.0, 0.0, 0.0])
    if ti.abs(n[1]) < 1 - 1e-3:
        u = n.cross(ti.Vector([0.0, 1.0, 0.0])).normalized()
    v = n.cross(u)
    phi = 2 * math.pi * ti.random(ti.f32)
    r = ti.random(ti.f32)
    ay = ti.sqrt(r)
    ax = ti.sqrt(1 - r)
    return ax * (ti.cos(phi) * u + ti.sin(phi) * v) + ay * n


@ti.func
def reflect(d, n):
    # Assuming |d| and |n| are normalized
    return d - 2.0 * d.dot(n) * n


@ti.func
def refract(d, n, ni_over_nt):
    # Assuming |d| and |n| are normalized
    has_r, rd = 0, d
    dt = d.dot(n)
    discr = 1.0 - ni_over_nt * ni_over_nt * (1.0 - dt * dt)
    if discr > 0.0:
        has_r = 1
        rd = (ni_over_nt * (d - n * dt) - n * ti.sqrt(discr)).normalized()
    else:
        rd *= 0.0
    return has_r, rd


@ti.func
def ray_aabb_intersection(box_min, box_max, o, d):
    intersect = 1

    near_int = -inf
    far_int = inf

    for i in ti.static(range(3)):
        if d[i] == 0:
            if o[i] < box_min[i] or o[i] > box_max[i]:
                intersect = 0
        else:
            i1 = (box_min[i] - o[i]) / d[i]
            i2 = (box_max[i] - o[i]) / d[i]

            new_far_int = ti.max(i1, i2)
            new_near_int = ti.min(i1, i2)

            far_int = ti.min(new_far_int, far_int)