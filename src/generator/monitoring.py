# -*- encoding: utf-8 -*-
"""
Desc      :   Place monitoring points on layout domain.
"""
# File    :   monitoring.py
# Time    :   2021/07/09 08:33:57
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn

import numpy as np
from src.data.base import Components, Domain
from .sampling import TaskPowersSampling, FMatrix


com_max = 200 # less than 200 monitoring points per component
region_max = 50000 # less than 50000 monitoring points on the region out of components
TOL = 1e-14


class Monitor:
    
    def __init__(self, components: Components, sampling_strategy):
        self.components = components
        self.sampling_strategy = sampling_strategy[0]

    def sampling(self):

        if self.sampling_strategy[0] =='random':
            assert len(self.sampling_strategy) == 2, 'Error random sampling!'
            num = self.sampling_strategy[1]
            position = self.random_sampling(num)

        elif self.sampling_strategy[0] == 'uniform':
            assert (len(self.sampling_strategy) == 2 or len(self.sampling_strategy) == 3), 'Error uniform sampling!'
            row = self.sampling_strategy[1]
            col = self.sampling_strategy[1] if (len(self.sampling_strategy) == 2) else self.sampling_strategy[2]
            position = self.uniform_sampling(row, col)

        elif self.sampling_strategy[0] == 'center':
            assert (len(self.sampling_strategy) in [2,3,4]), 'Error center sampling!'
            center_num = self.sampling_strategy[1]
            boundary_num = 0 if (len(self.sampling_strategy) == 2) else self.sampling_strategy[2]
            region_num = 0 if (len(self.sampling_strategy) in [2,3]) else self.sampling_strategy[3]
            position = self.center_sampling(center_num, boundary_num, region_num)
        
        else:
            LookupError(f'Sampling strategy {self.sampling_strategy[0]} is not supported (random,uniform,center)!')

        return position

    def random_sampling(self, num):
        # generate random number
        rand = np.arange(self.components.domain.grid*self.components.domain.grid)
        np.random.shuffle(rand)
        rand = rand.reshape(self.components.domain.grid, self.components.domain.grid)

        position = np.zeros_like(rand)
        position[np.where(rand<num)]=1
        return position

    def center_sampling(self, component_num, boundary_num, region_num):
        position = np.zeros((self.components.domain.grid, self.components.domain.grid))

        # on components
        task = TaskPowersSampling(self.components)
        fm = FMatrix(self.components, task.sample_intensity())

        assert component_num in range(0, com_max)
        if component_num == 0:
            pass
        elif component_num == 1:
            position[tuple(np.transpose(np.floor(np.flip(self.components.position/self.components.domain.size*self.components.domain.grid, axis=1)).astype(np.int64)))] = 1
        else:
            position[tuple(np.transpose(np.floor(np.flip(self.components.position/self.components.domain.size*self.components.domain.grid, axis=1)).astype(np.int64)))] = 1
            for size_i, int_i, angle_i, geo_i, pd_i, pos_i in zip(self.components.size, task.sample_intensity(), self.components.angle, self.components.geometry, self.components.power_distribution, self.components.position):
                _, com_i = fm.rotate2matrix(size_i, int_i, angle_i, geo_i, pd_i, pos_i)
                seq_i = np.arange(com_i[np.where(com_i>TOL)].size)
                np.random.shuffle(seq_i)
                seq_i = seq_i[:component_num-1]
                grid_ix = np.where(com_i>TOL)[0]
                grid_iy = np.where(com_i>TOL)[1]
                grid_ix = grid_ix[seq_i]
                grid_iy = grid_iy[seq_i]
                position[tuple([grid_ix,grid_iy])] = 1

        # on boundary
        assert boundary_num in range(0, self.components.domain.grid)
        if boundary_num == 0:
            pass
        elif boundary_num == 1:
            mesh = [np.floor(self.components.domain.grid/2).astype(np.int64)]
        else:
            mesh = list(range(0,self.components.domain.grid+1,np.floor(self.components.domain.grid/(boundary_num-1)).astype(np.int64)))
            if mesh[-1]==self.components.domain.grid:
                mesh[-1]-=1
        position[mesh, 0] = 1
        position[0, mesh] = 1
        position[self.components.domain.grid-1, mesh] = 1
        position[mesh, self.components.domain.grid-1] = 1

        # on other region
        assert region_num in range(0, region_max)
        if region_num == 0:
            pass
        else:
            com_area = task.overlap
            seq = np.arange(com_area[np.where(com_area<TOL)].size)
            np.random.shuffle(seq)
            seq = seq[:region_num]
            grid_x = np.where(com_area<TOL)[0]
            grid_y = np.where(com_area<TOL)[1]
            grid_x = grid_x[seq]
            grid_y = grid_y[seq]
            position[tuple([grid_x,grid_y])] = 1

        return position

    def uniform_sampling(self, row, col):
        position = np.zeros((self.components.domain.grid, self.components.domain.grid))
        assert row in range(1, self.components.domain.grid), 'Wrong uniform sampling'
        assert col in range(1, self.components.domain.grid), 'Wrong uniform sampling'
        if row == 1:
            grid_x = [np.floor(self.components.domain.grid/2).astype(np.int64)]
        else:
            grid_x = list(range(0,self.components.domain.grid+1,np.floor(self.components.domain.grid/(row-1)).astype(np.int64)))
            if grid_x[-1]==self.components.domain.grid:
                grid_x[-1]-=1
        if col == 1:
            grid_y = [np.floor(self.components.domain.grid/2).astype(np.int64)]
        else:
            grid_y = list(range(0,self.components.domain.grid+1,np.floor(self.components.domain.grid/(col-1)).astype(np.int64)))
            if grid_y[-1]==self.components.domain.grid:
                grid_y[-1]-=1
        
        monitoring_mesh = np.meshgrid(np.array(grid_x),np.array(grid_y))
        position[tuple(monitoring_mesh)] = 1

        return position