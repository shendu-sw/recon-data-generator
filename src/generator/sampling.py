# -*- encoding: utf-8 -*-
"""
Desc      :   Power Sampling.
"""
# File    :   sampling.py
# Time    :   2021/07/09 08:33:57
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn

import sys
import math
import numpy as np
from typing import Sequence

from src.data.base import Task, Components, Domain


TOL = 1e-10


class TaskPowersSampling(Task):
    def __init__(self, components: Components):
        super(TaskPowersSampling, self).__init__(components)
        self.overlap = None
        self.F = None
        self.sample()

    def sample(self):
        """在给定布局情况下，随机对功率进行采样，获得布局对应的F"""

        intensity = self.sample_intensity()
        self.F, self.overlap = FMatrix(self.components, intensity).com2matrix()
        return self.F, True

    def is_overlaping(self):
       return (np.array(self.overlap) > 1 + 1e-5).any()

    def sample_intensity(self):
        """在给定布局情况下，随机对功率进行采样"""

        intensity = []
        for p in self.components.intensity:
            if isinstance(p[0], str):
                if p[0] == "uniform":  # 对功率进行区间内的随机采样
                    if len(p) == 3:  # ["uniform", 10000, 20000]
                        intensity.append(
                            np.random.uniform(low=p[1], high=p[2])
                        )
                    elif (
                        len(p) == 4
                    ):  # ["uniform", 10000, 20000, interval=100]
                        choice = range(p[1], p[2] + 1, p[3])
                        intensity.append(np.random.choice(choice))
                    else:
                        raise ValueError(
                            "The data format of powers is not right."
                        )
                elif p[0] == "normal":
                    intensity.append(
                        np.random.normal(p[1], p[2])
                    )
                elif p[0] == "lognormal":
                    mean = p[1]
                    std = p[2]
                    var = std ** 2
                    mu = math.log(mean ** 2 / math.sqrt(mean ** 2 + var))
                    std = math.sqrt(math.log(1 + var / mean ** 2))
                    intensity.append(
                        np.random.lognormal(mu, std)
                    )
                elif p[0] == "gumbel":
                    mean = p[1]
                    std = p[2]
                    var = std ** 2
                    belta = math.sqrt(6 * var / (math.pi ** 2))
                    mu = mean - 0.57721 * belta
                    intensity.append(
                        np.random.gumbel(mu, belta)
                    )
                else:
                    raise LookupError(f"Method {p[0]} does not supported!")
            else:
                intensity.append(np.random.choice(p))
        self.intensity_sample = intensity
        return self.intensity_sample


class FMatrix:

    def __init__(self, components: Components, sample_power):

        self.components = components
        self.sample_power = sample_power
        self.comgrid = None
        self.overlap = None

    def com2matrix(self):

        self.comgrid = np.zeros((self.components.domain.grid,self.components.domain.grid))
        self.overlap = np.zeros((self.components.domain.grid,self.components.domain.grid))

        special_zero = special_random_num(self.components.number, self.components.special_num, special=self.components.special)
        constant_power = self.sample_power[0]

        for num, size_i, int_i, angle_i, geo_i, pd_i, pos_i in zip(range(0,self.components.number), self.components.size, self.sample_power, self.components.angle, self.components.geometry, self.components.power_distribution, self.components.position):
            # special heat source components
            if self.components.special == "y" and self.components.special_num == self.components.number:
                int_i = constant_power
            elif num in special_zero:
                continue
            else:
                pass

            comgrid, overlap = self.rotate2matrix(size_i, int_i, angle_i, geo_i, pd_i, pos_i)

            self.comgrid = self.comgrid + comgrid
            self.overlap = self.overlap + overlap

        return self.comgrid, self.overlap

    def rotate2matrix(self, size, intensity, angle, geometry, power_distribution, position):

        if geometry == 'rectangle':
            comgrid, overlap = self.rectangle2matrix(size, intensity, angle, geometry, power_distribution, position)
        elif geometry == 'circle':
            comgrid, overlap = self.circle2matrix(size, intensity, angle, geometry, power_distribution, position)
        elif geometry == 'capsule':
            comgrid, overlap = self.capsule2matrix(size, intensity, angle, geometry, power_distribution, position)
        else:
            raise LookupError(f'Geometry {geometry} is not supported (rectangle,circle,capsule)!')
                
        # rotate
        if abs(angle) <= TOL:
            comgrid, overlap = comgrid[self.components.domain.grid:-self.components.domain.grid,self.components.domain.grid:-self.components.domain.grid], \
                                overlap[self.components.domain.grid:-self.components.domain.grid,self.components.domain.grid:-self.components.domain.grid]
        else:
            comgrid, overlap = component_rotate(position, size, angle, self.components.domain.size, \
                                                self.components.domain.grid, comgrid, overlap)
        return comgrid, overlap

    def rectangle2matrix(self, size, intensity, angle, geometry, power_distribution, position):
        comgrid = np.zeros((3*self.components.domain.grid,3*self.components.domain.grid))
        overlap = np.zeros((3*self.components.domain.grid,3*self.components.domain.grid))

        lp = position - size/2
        rp = position + size/2
        if angle <= TOL:
            assert lp[0]>0 and lp[1]>0 and rp[0]<=self.components.domain.size and rp[1]<=self.components.domain.size
        else:
            assert max(lp[0],lp[1])>=0 and min(rp[0],rp[1])<=self.components.domain.size and min(lp[0],lp[1])>-self.components.domain.size and max(rp[0],rp[1])<=2*self.components.domain.size
        lp_grid = np.round(lp/self.components.domain.size * self.components.domain.grid).astype(np.int64)
        rp_grid = np.round(rp/self.components.domain.size * self.components.domain.grid).astype(np.int64)

        rn = pow((lp[0]-position[0]),2)+pow((lp[1]-position[1]),2)

        for col in range(lp_grid[0],rp_grid[0]):
            for row in range(lp_grid[1],rp_grid[1]):
                overlap[row+self.components.domain.grid,col+self.components.domain.grid] += 1
                if power_distribution == 'uniform':
                    comgrid[row+self.components.domain.grid,col+self.components.domain.grid] = self.uniform2matrix(intensity)
                elif power_distribution == 'gaussian':
                    comgrid[row+self.components.domain.grid,col+self.components.domain.grid] = self.gaussian2matrix(row, col, position, intensity, rn, self.components.gaussian_param)
                else:
                    raise LookupError(f'Power distribution {power_distribution} is not supported (gaussian, uniform)!')
        return comgrid, overlap

    def circle2matrix(self, size, intensity, angle, geometry, power_distribution, position):
        comgrid = np.zeros((3*self.components.domain.grid,3*self.components.domain.grid))
        overlap = np.zeros((3*self.components.domain.grid,3*self.components.domain.grid))

        lp = position - size/2
        rp = position + size/2
        if angle <= TOL:
            assert lp[0]>0 and lp[1]>0 and rp[0]<=self.components.domain.size and rp[1]<=self.components.domain.size
        else:
            assert min(lp[0],lp[1])>=0 and max(rp[0],rp[1])<=self.components.domain.size and min(lp[0],lp[1])>-self.components.domain.size and max(rp[0],rp[1])<=2*self.components.domain.size
        lp_grid = np.round(lp/self.components.domain.size * self.components.domain.grid).astype(np.int64)
        rp_grid = np.round(rp/self.components.domain.size * self.components.domain.grid).astype(np.int64)

        rn = pow(size[0]/2,2) if size[0]>=size[1] else pow(size[1]/2,2)

        for col in range(lp_grid[0],rp_grid[0]):
            for row in range(lp_grid[1],rp_grid[1]):
                dis = pow((col/self.components.domain.grid*self.components.domain.size-position[0]),2)/ pow(size[0]/2,2)+pow((row/self.components.domain.grid*self.components.domain.size-position[1]),2)/ pow(size[1]/2,2)
                if dis < 1:
                    overlap[row+self.components.domain.grid,col+self.components.domain.grid] += 1
                    if power_distribution == 'uniform':
                        comgrid[row+self.components.domain.grid,col+self.components.domain.grid] = self.uniform2matrix(intensity)
                    elif power_distribution == 'gaussian':
                        comgrid[row+self.components.domain.grid,col+self.components.domain.grid] = self.gaussian2matrix(row, col, position, intensity, rn, self.components.gaussian_param)
                    else:
                        raise LookupError(f'Power distribution {power_distribution} is not supported (gaussian, uniform)!')
                else:
                    pass
        return comgrid, overlap

    def capsule2matrix(self, size, intensity, angle, geometry, power_distribution, position):
        comgrid = np.zeros((3*self.components.domain.grid,3*self.components.domain.grid))
        overlap = np.zeros((3*self.components.domain.grid,3*self.components.domain.grid))

        lp = position - size/2
        rp = position + size/2
        if abs(angle) <= TOL:
            assert lp[0]>0 and lp[1]>0 and rp[0]<=self.components.domain.size and rp[1]<=self.components.domain.size
        else:
            assert min(lp[0],lp[1])>=0 and max(rp[0],rp[1])<=self.components.domain.size and min(lp[0],lp[1])>-self.components.domain.size and max(rp[0],rp[1])<=2*self.components.domain.size
        lp_grid = np.round(lp/self.components.domain.size * self.components.domain.grid).astype(np.int64)
        rp_grid = np.round(rp/self.components.domain.size * self.components.domain.grid).astype(np.int64)

        rn = pow(size[0]/2,2) if size[0]>=size[1] else pow(size[1]/2,2)

        for col in range(lp_grid[0],rp_grid[0]):
            for row in range(lp_grid[1],rp_grid[1]):
                row_d = row/self.components.domain.grid*self.components.domain.size
                col_d = col/self.components.domain.grid*self.components.domain.size

                ll = (position[0] - (size[0]-size[1])/2, position[1]-size[1]/2) if size[0] > size[1] else (position[0] - (size[0])/2, position[1]-(size[1]-size[0])/2)
                rr = (position[0] + (size[0]-size[1])/2, position[1]+size[1]/2) if size[0] > size[1] else (position[0] + (size[0])/2, position[1]+(size[1]-size[0])/2)
                
                lc = (position[0]-(size[0]-size[1])/2, position[1]) if size[0] > size[1] else (position[0], position[1]-(size[1]-size[0])/2)
                rc = (position[0]+(size[0]-size[1])/2, position[1]) if size[0] > size[1] else (position[0], position[1]+(size[1]-size[0])/2)
                dlc = pow((col/self.components.domain.grid*self.components.domain.size-lc[0]),2)+pow((row/self.components.domain.grid*self.components.domain.size-lc[1]),2)
                drc = pow((col/self.components.domain.grid*self.components.domain.size-rc[0]),2)+pow((row/self.components.domain.grid*self.components.domain.size-rc[1]),2)
                        
                radius = size[0]/2 if size[0]<=size[1] else size[1]/2
                        
                if (ll[0] <= col_d and col_d <= rr[0] and ll[1] <= row_d and row_d <= rr[1]) or dlc <= pow(radius,2) or drc <= pow(radius,2):
                    overlap[row+self.components.domain.grid,col+self.components.domain.grid] += 1
                    if power_distribution == 'uniform':
                        comgrid[row+self.components.domain.grid,col+self.components.domain.grid] = self.uniform2matrix(intensity)
                    elif power_distribution == 'gaussian':
                        comgrid[row+self.components.domain.grid,col+self.components.domain.grid] = self.gaussian2matrix(row, col, position, intensity, rn, self.components.gaussian_param)
                    else:
                        raise LookupError(f'Power distribution {power_distribution} is not supported (gaussian, uniform)!')
                else:
                    pass
        return comgrid, overlap

    def uniform2matrix(self, intensity):
        return intensity

    def gaussian2matrix(self, row, col, position, intensity, rn, gaussian_param):
        point_dis = pow((col/self.components.domain.grid*self.components.domain.size-position[0]),2)+pow((row/self.components.domain.grid*self.components.domain.size-position[1]),2)
        return intensity*np.exp(-gaussian_param*point_dis/rn)


# special components random selected
def special_random_num(
    num: int,
    num_zero: int,
    special='n',
):
    if special == 'y':
        s = [x for x in range(0,num)]
        import random
        random.shuffle(s)
        assert num_zero in range(0,num+1), "Wrong number of special heat sources"
        if num_zero==0 or num_zero==num:
            return []
        else:
            return s[:num_zero]
    else:
        return []


# components rotate operation
def component_rotate(
    center,
    size, 
    angle, 
    length, 
    grid,
    comgrid, 
    overlap
):
    rotate_comgrid = np.zeros_like(comgrid)
    rotate_overlap = np.zeros_like(overlap)

    size_m = max(size) * 1.5
    
    lp = center - size_m/2
    rp = center + size_m/2

    lp_grid = np.round(lp/length * grid).astype(np.int64)
    rp_grid = np.round(rp/length * grid).astype(np.int64)

    for col in range(lp_grid[0], rp_grid[0]):
        for row in range(lp_grid[1], rp_grid[1]):

            poi = [col/grid*length, row/grid*length]
            m = dis(poi, center)
            pA = math.asin((poi[1]-center[1])/(m+TOL))
            p0 = math.radians(180)
            pr = math.radians(angle)
            dy = m * math.sin(p0-pA-pr) if poi[0] < center[0] else m * math.sin(pA-pr)
            dx = m * math.cos(p0-pA-pr) if poi[0] < center[0] else m * math.cos(pA-pr)
            x = center[0] + dx
            y = center[1] + dy
            
            if ((math.floor(x/length*grid)+grid) in range(lp_grid[0]+grid, rp_grid[0]+grid)) and ((math.floor(y/length*grid)+grid) in range(lp_grid[1]+grid, rp_grid[1]+grid)):
                rotate_overlap[row+grid, col+grid] = overlap[math.floor(y/length*grid)+grid, math.floor(x/length*grid)+grid]
                rotate_comgrid[row+grid, col+grid] = comgrid[math.floor(y/length*grid)+grid, math.floor(x/length*grid)+grid]
            else:
                pass
    if lp_grid.all() in range(0,grid) and rp_grid.all() in range(0,grid):
        pass
    else:
        if lp_grid[0] < -TOL:
            assert abs(rotate_overlap[..., lp_grid[0]+grid:grid]).all() < TOL
        elif lp_grid[1] < -TOL:    
            assert rotate_overlap[lp_grid[1]+grid:grid, ...].all() < TOL
        elif rp_grid[0]>grid+TOL:
            assert abs(rotate_overlap[..., grid:rp_grid[0]+grid]).all() < TOL
        elif rp_grid[1]>grid+TOL:
            assert rotate_overlap[grid+rp_grid[1]+grid, ...].all() < TOL
        else:
            pass

    return rotate_comgrid[grid:-grid,grid:-grid], rotate_overlap[grid:-grid,grid:-grid]


def dis(point, center):
    return np.linalg.norm(np.array(point-center))


def get_task_powers_sampling(
    geometry_board: str,
    size_board: float,
    grid_board: int,
    geometry: Sequence,
    size: Sequence,
    angle: Sequence,
    intensity: Sequence,
    power_distribution: Sequence,
    position: Sequence,
    special: str = "n",
    special_num=0,
    gaussian_param=1,
    rad=True,
    method: str = "random",
) -> Task:
    """构造布局任务

    Args:
        geometry_board (str): [description]
        size_board (float): [description]
        grid_board (int): [description]
        geometry (Sequence): [description]
        size (Sequence): [description]
        angle (Sequence): [description]
        intensity (Sequence): [description]
        position (Sequence, optional): [description].
        rad (bool, optional): [description]. Defaults to True.
        method (str, optional): [description]. Defaults to "random".

    Returns:
        Task: [description]
    """

    domain = Domain(geometry_board, size_board, grid_board)
    components = Components(
        domain, geometry, size, angle, intensity, power_distribution, position, special_num=special_num, special=special
    )
    if method == "random":
        return TaskPowersSampling(components)
    elif method is None:
        return Task(components)
    else:
        raise LookupError(f"Method {method} does not supported!")

