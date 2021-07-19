# -*- encoding: utf-8 -*-
"""
Desc      :   Base definition of problem.
"""
# File    :   base.py
# Time    :   2021/07/09 08:33:57
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn

import numpy as np
from typing import Sequence


class Domain:
    """布局区域信息
    """

    def __init__(self, geometry="s", size=0.1, grid=200):
        self.geometry = geometry  # 定义布局区域的形状 s-square
        self.size = size  # unit: m
        self.grid = grid  # 定义划分网格数量


class Components:
    """组件信息
    """

    def __init__(
        self,
        domain: Domain,
        geometry: Sequence,
        size: Sequence,
        angle: Sequence,
        intensity: Sequence,
        power_distribution: Sequence,
        position: Sequence,
        special_num=0,
        special=False,
        gaussian_param=1,
        rad=True,
    ):
        assert (
            len(size) == len(intensity) == len(angle) == len(geometry) == len(power_distribution) == len(position)
        ), "Size, intensity, angle, geometry, power_distribution and positions must have the same length."
        self.domain = domain
        # ###################### user defines components here #########
        # 's': square 'r': rectangle
        self.geometry = geometry
        self.number = len(geometry)
        # 先写长边，再写短边，长边与x轴方向的夹角为其摆放角度
        # 例如某组件 x方向的边长 0.1，y方向的边长为 0.2，故其size=[0.2 0.1],angle = pi/2
        # the length and width of components, unit : m
        self.size = np.array(size)
        self.position = np.array(position)
        # the angle of placement

        self.angle = np.array(angle)
        # 角度 -> 弧度
        if not rad:
            self.angle = self.angle / 180 * np.pi

        # heat disapation power: W
        self.intensity = [
            (p if isinstance(p, list) else [p]) for p in intensity
        ]
        self.power_distribution = power_distribution

        # define the given position from yaml file
        if position is not None:
            assert len(position) == self.number
            self.given_position = position
        else:
            self.given_position = position
        # ###################### user defines components here ###########

        self.size_pixel = np.rint((self.size / domain.size) * domain.grid)
        # self.intensity_norm = self.intensity / np.max(
        #     self.intensity
        # )  # normalized


        # 计算旋转角度以后对应  x 轴边长，y 轴边长
        self.realsize = (
            np.reshape(np.cos(self.angle), [-1, 1]) * self.size
            + np.reshape(np.sin(self.angle), [-1, 1]) * self.size[:, ::-1]
        )
        self.realsize_pixel = np.rint(
            (self.realsize / domain.size) * domain.grid
        )
        #self.comgrid = None
        #self.com2matrix()

        self.gaussian_param = gaussian_param

        # 特殊样本
        self.special = special
        self.special_num = special_num

    @property
    def real_area(self):
        """组件实际面积 real_x*real_y"""
        return np.prod(self.realsize, axis=1)

    def __len__(self):
        return self.number


class Task:
    """温度场重建任务"""

    def __init__(self, components: Components):
        self.domain = components.domain
        self.components = components
        self.location = np.zeros((components.number, 2))
        self.angle = components.angle
        self.given_position = components.given_position
        self.intensity_sample = []

    def sample(self, *args):
        raise NotImplementedError