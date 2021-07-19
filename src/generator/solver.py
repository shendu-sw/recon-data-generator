# -*- encoding: utf-8 -*-
"""
Desc      :   solver for TFR-HSS task.
"""
# File    :   solver.py
# Time    :   2021/07/08 09:07:46
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn


import numpy as np

import fenics as fs
from src.generator.boundary import AllBoundary


TOL = 1e-14


class Source(fs.UserExpression):
    def __init__(self, F, length):
        """

        Args:
            F (ndarray): 热源矩阵，2d or 3d
            length (float): 板边长
        """
        super().__init__(self)
        self.F = F
        self.ndim = F.ndim
        self.length = length

    def eval(self, value, x):
        value[0] = self.get_source(x)

    def get_source(self, x):
        """由预生成的 F 获取热源函数值 f(x).

        Args:
            x : 坐标

        Returns:
            float: 热源函数值 f(x)
        """
        assert self.ndim in [2, 3]
        n = self.F.shape[0]
        if self.ndim == 2:
            xx = int(x[0] / self.length * (n - 1))
            yy = int(x[1] / self.length * (n - 1))
            return self.F[yy, xx]
        xx = int(x[0] / self.length * (n - 1))
        yy = int(x[1] / self.length * (n - 1))
        zz = int(x[2] / self.length * (n - 1))
        return self.F[zz, yy, xx]

    def value_shape(self):
        return ()


def get_mesh(length, nx, ny, nz=None):
    """generate mesh: support rectangle, Box (not supported)

    """
    if nz is None:
        mesh = fs.RectangleMesh(
            fs.Point(0.0, 0.0), fs.Point(length, length), nx, ny
        )
    else:
        mesh = fs.BoxMesh(
            fs.Point(0.0, 0.0, 0.0),
            fs.Point(length, length, length),
            nx,
            ny,
            nz,
        )
    return mesh


def get_mesh_grid(length, nx, ny, nz=None):
    """provide the coordinates of the mesh grid

    """
    mesh = get_mesh(length, nx, ny, nz)
    if nz is None:
        xs = mesh.coordinates()[:, 0].reshape(ny + 1, nx + 1).T
        ys = mesh.coordinates()[:, 1].reshape(ny + 1, nx + 1).T
        return xs, ys, None
    xs = mesh.coordinates()[:, 0].reshape(nx + 1, ny + 1, nz + 1)
    ys = mesh.coordinates()[:, 1].reshape(nx + 1, ny + 1, nz + 1)
    zs = mesh.coordinates()[:, 2].reshape(nx + 1, ny + 1, nz + 1)
    return xs, ys, zs


def solver(f, length, bds, u_D, Nx, Ny, degree=1):
    """
    Solve -Laplace(u) = f on [0,1] x [0,1] with 2*Nx*Ny Lagrange
    elements of specified degree and u = u_D (Expresssion) on
    the boundary.
    """

    # Create mesh and define function space
    mesh = get_mesh(length, Nx, Ny)
    V = fs.FunctionSpace(mesh, 'P', degree)

    if bds:
        bcs = AllBoundary(V, bds, u_D).get_boundary()  
    else:
        ValueError('Boundary conditions empty!')

    # Define variational problem
    u = fs.TrialFunction(V)
    v = fs.TestFunction(V)
    F = fs.dot(fs.grad(u), fs.grad(v))*fs.dx - f*v*fs.dx
    a = fs.lhs(F)
    L = fs.rhs(F)

    # Compute solution
    u = fs.Function(V)
    fs.solve(a == L, u, bcs)
    return u


def run_solver(
    ndim,
    length,
    units,
    bcs,
    u0,
    nx,
    F,
    coordinates=False,
    is_plot=False,
    vtk=False,
):
    "Run solver to compute and post-process solution"

    ny = nx
    nz = nx if ndim == 3 else None

    # Set up problem parameters and call solver
    f = Source(F, length)
    u = solver(f, length, bcs, u0, nx, ny, degree=1)

    if is_plot:
        import matplotlib.pyplot as plt

        plt.plot(u)
    if vtk:
        vtkfile = fs.File("solution.pvd")
        vtkfile << u
    if ndim == 2:
        U = u.compute_vertex_values().reshape(nx + 1, nx + 1)
    else:
        U = u.compute_vertex_values().reshape(nx + 1, nx + 1, nx + 1)
    
    if coordinates:
        xs, ys, zs = get_mesh_grid(length, nx, ny, nz)
    else:
        xs, ys, zs = None, None, None
    return U, xs, ys, zs


if __name__ == '__main__':
    u0 = 298
    um = 25
    mesh_row = 199
    mesh_line = 199
    sine_direction = 'u'
    length = 0.1
    run_solver(u0, um, mesh_row, mesh_line, sine_direction, length)