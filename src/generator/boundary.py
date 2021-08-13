# -*- encoding: utf-8 -*-
'''
Desc      :   Boundary definition
'''
# File    :   boundary.py
# Time    :   2021/07/09 08:33:57
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn

import fenics as fs
import numpy as np


TOL = 1e-10


class AllBoundary:
    """边界定义

    """

    def __init__(self, V, bds, u_D=298):

        self.bds = bds
        self.u_D = u_D
        self.V = V

    def get_boundary(self):
        bcs = []
        for bd in self.bds:
            assert (len(bd) == 2 or len(bd) == 3), 'Error Boundary!'
            if bd[0] == 'sink':
                u0 = self.u_D if len(bd)==2 else bd[2]
                boundary = LineBoundary(bd[1],u0)
                bc = fs.DirichletBC(self.V, boundary.expression(), boundary.get_boundary())
                bcs.append(bc)
            elif bd[0] == 'sine-wave':
                u0 = self.u_D if len(bd)==3 else bd[2]
                um = bd[2] if len(bd)==3 else bd[3]
                boundary = SineBoundary(bd[1],u0,um)
                bc = fs.DirichletBC(self.V, boundary.expression(), boundary.get_boundary())
                bcs.append(bc)
            else:
                LookupError(f'Boundary condition {bc[0]} is not supported (sink, sine-wave)!')
        return bcs


class LineBoundary:
    """线段边界

    Args:
        line (list): 表示边界的线段，格式为 [[起点x, 起点y], [终点x, 终点y]]
        u0: 表示温度值
    """

    def __init__(self, line, u0):

        self.line = line
        self.u0 = u0
        assert len(line) == 2, "线段包含两个点"
        assert len(line[0]) == 2 and len(line[1]) == 2, "二维点"
        length = abs(np.array(line[1])-np.array(line[0]))
        assert (length[0] < TOL or length[1]<TOL), 'Line boundary is not on boundary!'

    def expression(self):
        u_D = fs.Constant(self.u0)
        return u_D

    def get_boundary(self):
        """构造 fenics 所需 bc 函数

        Returns:
            function: fenics 所需 bc
        """

        def boundary(x, on_boundary):
            if on_boundary:
                (lx, ly), (rx, ry) = self.line
                if (lx - TOL <= x[0] <= rx + TOL) and (
                    ly - TOL <= x[1] <= ry + TOL
                ):
                    return True
            return False

        return boundary


class SineBoundary:
    """Sine-wave Distribution boundary

    Args:
        interval: 表示边界区间
        u0: 表示基础温度
        um: 表示sine-wave温度波动范围
    """

    def __init__(self, interval, u0, um):

        self.interval = np.array(interval)
        self.u0 = u0
        self.um = um
        self.length = abs(self.interval[1]-self.interval[0])
        #print(self.u0,self.um,self.interval)

    def expression(self):
        assert (self.length[0] < TOL or self.length[1]<TOL), 'Sine boundary is not on boundary!'
        length = max(self.length)
        
        u_D = fs.Expression('um*sin((x[0]-t0)*pi/length)+u0', \
            degree=2, t0=self.interval[0,0],length=length, um=self.um, u0=self.u0) \
            if self.length[1]<TOL else \
            fs.Expression('um*sin((x[1]-t0)*pi/length)+u0', \
            degree=2, t0=self.interval[0,1],length=length, um=self.um, u0=self.u0)
        return u_D

    def get_boundary(self):
        """构造 fenics 所需 bc 函数

        Returns:
            function: fenics 所需 bc
        """

        def boundary(x, on_boundary):

            if on_boundary:
                (lx, ly), (rx, ry) = self.interval
                if (lx - TOL <= x[0] <= rx + TOL) and (
                    ly - TOL <= x[1] <= ry + TOL
                ):
                    return True
            return False

        return boundary
