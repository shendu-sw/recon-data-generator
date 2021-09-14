# Data Generator for Temperature Field Reconstruction of Heat Source Systems

![](https://img.shields.io/github/issues/shendu-sw/recon-data-generator)![](https://img.shields.io/github/license/shendu-sw/recon-data-generator)

> This project is based on [FEniCS](https://fenicsproject.org) and used for data generation of temperature field reconstruction samples. This data generator mainly supports the paper "[A Machine Learning Modelling Benchmark for Temperature Field Reconstruction of Heat-Source Systems](https://arxiv.org/abs/2108.08298)"

## Samples

![1](https://i.loli.net/2021/07/19/xFHNAzykSqICgpR.png)

## Support functions

* Configurations
    * [x] Size of board
        * [x] 2-D
            * [x] `length`
            * [x] `width` (default: equal to length）
    * [x] Scale Number
        * [x] mesh grid（`nx`）
    * [x] Boundary Conditions（`bcs`）
        * [x] Heat Sink (Dirichlet BC) 
        * [x] Sine function boundary (Dirichlet BC )
        * [x] default (Neumann BC)
    * [x] Components
        * [x] type
            * [x] `rectangle`
            * [x] `circle`
            * [x] `capsule`
            * [ ] triangle
        * [x] size of units
            * [x] length
            * [x] width
        * [x] powers
            * [x] constant
            * [x] one from a given set
            * [x] uniform sampling
        * [x] 功率类型
            * [x] 固定功率
            * [x] 高斯分布功率
        * [x] 组件位置和角度
            * [x] 组件中心位置坐标（positions）
            * [x] 组件放置角度（angles）
        * [x] 组件数量
    * [x] 存储格式
        * [x] mat格式
    * [x] 测点选取策略
        * [x] random
        * [x] uniform
        * [x] center
        * [x] from_mat（从mat文件中读取，默认读取变量为u_pos）
    * [x] 特殊样本
        * [x] 打开关闭（special）
        * [x] 特殊组件数量（功率为0的组件数量，全部组件情况为所有组件功率相同）

## Installation

本生成器依赖 fenics 作为有限元求解器，可参照 [fenics 安装文档](https://fenicsproject.org/download/)，推荐以下**两种**方式安装，如果没有 docker 使用经验推荐 Anaconda 方式

- Anaconda (**Linux**， **Mac**)

  1. 使用 `conda` 创建并激活环境

  ```
  conda create -n fenicsproject -c conda-forge fenics mshr
  source activate fenicsproject
  ```

  1. use pip to install the released version

     - `pip install -U recon-data-generator`
     - or use unreleased version from master branch

     ```
     pip install -U git+https://github.com/shendu-sw/recon-data-generator.git
     ```

- Docker (**Linux**, **Win**, **Mac**)

## FAQ

- Windows 下可以使用 Docker 方式安装，或在应用商店安装 Ubuntu WSL

- pip 安装前可使用国内源如清华

  ```
  pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
  ```

- 仅支持 Python3.6 以上版本

- 如果按照以上 anaconda 安装方式，别忘了切换到 `fenicsproject` 环境

## Visualization

* 可视化生成配置文件入口`config_generate.html`
* For example:

| ![image-20210824224114153](https://i.loli.net/2021/08/24/qw2gyjI8sVld49v.png) | ![Example0](https://i.loli.net/2021/08/24/xXi8s3tYSqlMNGh.png)![Example1](https://i.loli.net/2021/08/24/BsLKHjGm98FaTEZ.png) |
| :----------------------------------------------------------: | :----------------------------------------------------------: |
|               heat source system visualization               |                  samples by data generator                   |

## Easy Starting

* `data generate`执行如下命令

```python
recon_data_generator generate
```

* `plot`执行如下命令

```
recon_data_generator plot
```

