# -*- encoding: utf-8 -*-
"""
Desc      :   Plot tools.
"""
# File    :   plot.py
# Time    :   2021/07/09 08:33:57
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn

import matplotlib.pyplot as plt
from functools import partial
from pathlib import Path
import tqdm
from multiprocessing import Pool
import scipy.io as sio
import numpy as np


TOL = 1e-14


def plot_mat(
    mat_path,
    plot=True,
    save=False,
    worker=None,
    figkwargs={"figsize": (21, 5)},
):
    """Plot mat files.

    Arguments:
        mat_path (Path) : mat files path

    Keyword Arguments:
        plot (bool) : whether to show plot (default: (True))
        save (bool or str) : whether to save figure, can be fig path (default: (False))
        figkwargs (dict) : figure kwargs (default: {{'figsize': (12, 5)}})
    """
    mat_path = Path(mat_path)
    assert mat_path.exists(), "Input path does not exist!"
    if mat_path.is_dir():
        plot_dir(mat_path, save, worker)
        return
    mat = sio.loadmat(mat_path)
    xs, ys, u, F, u_obs = mat["xs"], mat["ys"], mat["u"], mat["F"], mat["u_obs"]

    xs = xs
    ys = ys

    fig = plt.figure(**figkwargs)
    plt.subplot(132)
    # img = plt.pcolormesh(ys, xs, u, shading='auto')
    img = plt.contourf(ys, xs, u, levels=150,cmap='jet')
    plt.colorbar(img)
    plt.axis("image")
    plt.title("Real Temperature Field")

    plt.subplot(131)
    img = plt.pcolormesh(ys, xs, F, shading='auto')
    plt.colorbar(img)
    plt.axis("image")
    plt.title("Heat Source System")

    plt.subplot(133)
    img = plt.contourf(ys, xs, u_obs, levels=150,cmap='jet')
    plt.colorbar(img)
    plt.axis("image")
    plt.title("Monitoring Points")

    if plot:
        plt.show()
    if save:  # save png
        if save is True:
            img_path = mat_path.with_suffix(".png")
        else:  # save is path
            img_path = Path(save)
            if img_path.is_dir():  # save is dir
                img_path = (img_path / mat_path.name).with_suffix(".png")
        fig.savefig(img_path, dpi=100)
        plt.close()


def plot_dir(path, out, worker):
    """将 mat 数据生成 png 图像

    Arguments:
        path {Path} : dir path
        out {Path} : output dir path
        worker {int} : number of workers
    """
    path = Path(path)
    assert path.is_dir(), "Error! Arg path must be a dir."
    if out is None:
        out = True
    else:
        out = Path(out)
        print(out.absolute())
        if out.exists():
            assert Path(out).is_dir(), "Error! Arg out must be a dir."
        else:
            out.mkdir(parents=True)

    with Pool(worker) as pool:
        plot_mat_p = partial(plot_mat, plot=False, save=out)
        pool_iter = pool.imap_unordered(plot_mat_p, path.glob("*.mat"))
        for _ in tqdm.tqdm(
            pool_iter, desc=f"{pool._processes} workers's running"
        ):
            pass


def get_parser(parser):

    parser.add_argument("-p", "--path", type=str, help="file path")
    parser.add_argument("-o", "--output", type=str, help="output path")
    parser.add_argument(
        "--plot-off", action="store_false", help="turn off plot"
    )
    parser.add_argument(
        "--dir", action="store_true", default=False, help="path is dir"
    )
    parser.add_argument("--worker", type=int, help="number of workers")
    parser.add_argument("--test", action="store_true", help="test mode")
    # TODO 3D version
    return parser


if __name__ == '__main__':

    ex = sio.loadmat('example_dataset/Example2.mat')
    fig = plt.figure(figsize=(12,5))
    plt.subplot(121)
    plt.imshow(ex['F'])
    plt.colorbar()
    plt.subplot(122)
    plt.imshow(ex['u'])
    plt.colorbar()
    fig.savefig('output/hot.png', dpi=300)