import taichi as ti
import numpy as np
import utils
from engine.mpm_solver import MPMSolver

write_to_disk = False

# Try to run on GPU
ti.init(arch=ti.cuda, kernel_profiler=True)

gui = ti.GUI("MPM Benchmark", res=256, background_color=0x112F41)

mpm = MPMSolver(res=(256, 256, 256), size=1, unbounded=False)

particles = np.fromfile('benchmark_particles.bin', dtype=np.float32)
particles = particles.reshape(len(particles) // 3, 3)
print(len(particles))

mpm.add_particles(particles=particles,
                  material=MPMSolver.material_elastic,
                  color=0xFFFF00)

mpm.set_gravity((0, -20, 0))

for frame in range(1500):
    mpm.step(3e-3)
    particles = mpm.particle_info()
    np_x = particles['position'] / 1.0

    # simple camera transform
    screen_x = 