# -*- encoding: utf-8 -*-
"""
Desc      :   Data processing.
"""
# File    :   data_processing.py
# Time    :   2021/07/09 08:33:57
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn

from pathlib import Path
import numpy as np
import scipy.io as sio


def save(
    options, i, U, xs, ys, F, U_obs, monitoring, zs=None
):
    """存储数据"""
    data_dir = Path(options.data_dir)
    file_name = f"{options.prefix}{i}"
    path = data_dir / file_name
    if options.file_format == "mat":
        path = path.with_suffix(".mat")
        save_mat(
            path,
            U,
            xs,
            ys,
            F,
            U_obs,
            monitoring,
            zs=zs,
        )


def save_mat(path, U, xs, ys, F, U_obs, monitoring, zs=None):
    # 组件位置从 1 开始
    zs = zs if zs is not None else []
    data = {
        "u": U,
        "xs": xs,
        "ys": ys,
        "zs": zs,
        "F": F,
        "u_obs": U_obs,
        "u_pos": monitoring
    }
    sio.savemat(path, data)


def load_mat(path):
    path = Path(path)
    assert path.suffix == ".mat"
    return sio.loadmat(path)