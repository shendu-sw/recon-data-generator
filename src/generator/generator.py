# -*- encoding: utf-8 -*-
"""
Desc      :   Main function for generator.
"""
# File    :   generator.py
# Time    :   2021/07/09 08:33:57
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn

from functools import partial
import numpy as np
import tqdm
import configargparse
from scipy.interpolate import griddata
from multiprocessing import Pool, Queue
import matplotlib.pyplot as plt

from src.generator.solver import run_solver
import src.data.data_processing as data_processing
from src.generator.sampling import get_task_powers_sampling
from src.generator.monitoring import Monitor


TOL = 1e-5


def generate_from_cli(options: configargparse.Namespace):
    """Generate from cli with options.

    Arguments:
        options (configargparse.Namespace): config options
    """
    print('Starting...')
    if options.bcs is None:
        options.bcs = []
    np.random.seed(options.seed)
    seeds = np.random.randint(2 ** 32, size=options.worker)
    seeds_q: Queue = Queue()
    for seed in seeds:
        seeds_q.put(seed)

    unit_n = len(options.units)

    positions = np.array([k for k in options.positions])
    if options.positions_type == "coord":
        pass
    elif options.positions_type == "grid":
        positions = positions / (options.nx + 1) * options.length
    else:
        raise LookupError(f"Type {options.positions_type} is not supported!")

    task = get_task_powers_sampling(
        geometry_board="s",
        size_board=options.length,
        grid_board=options.nx + 1,
        geometry=options.geometry,
        size=options.units,
        angle=options.angles,
        intensity=options.powers,
        power_distribution=options.power_distribution,
        position=positions,
        gaussian_param=options.gaussian_param,
        special = options.special,
        special_num = options.special_num,
        rad=False,
    )

    PMonitor = Monitor(task.components, options.monitoring_sampling)

    if options.method == "fenics":
        # 创建单参数函数

        method_fenics_p = partial(
            method_fenics,
            options=options,
            sampler=task.sample,
            task=task,
            monitor=PMonitor.sampling(),
        )

        # multiprocess support
        with Pool(
            options.worker, initializer=pool_init, initargs=(seeds_q,)
        ) as pool:
            pool_it = pool.imap(method_fenics_p, range(options.sample_n))
            # for i in pool_it:
            #     print(i)
            for _ in tqdm.tqdm(
                pool_it,
                desc=f"{pool._processes} workers's running",
                total=options.sample_n,
                ncols=100,
            ):
                pass

    print(f"Generated {options.sample_n} layouts in {options.data_dir}")


def pool_init(seeds_q):
    seed = seeds_q.get()
    np.random.seed(seed)


def method_fenics(i, options, sampler, task, monitor):
    """采用 fenics 求解"""
    while True:
        F, flag = sampler()
        intensity = task.intensity_sample
        if flag:
            break
    if task.is_overlaping():
        raise ValueError('Existing overlaping, Layout Error!')
    U, xs, ys, zs = run_solver(
        options.ndim,
        options.length,
        options.units,
        options.bcs,
        options.u_D,
        options.nx,
        F,
        coordinates=True,
    )

    U_obs = U * monitor

    data_processing.save(options, i, U, xs, ys, F, U_obs, monitor)

