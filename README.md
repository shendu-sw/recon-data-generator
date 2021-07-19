# Data Generator for Temperature Field Reconstruction of Heat Source Systems

> This project is based on [FEniCS](https://fenicsproject.org) and used for data generation of temperature field reconstruction samples.

## 样例（samples）

![1](https://i.loli.net/2021/07/19/5Kv4xTfXQza8yFC.png)

## 功能支持（Support functions）

* 可配置选项
    * [ ] 布局板尺寸
        * [x] 二维
            * [x] 长（length）
            * [x] 宽（默认等于length）
    * [ ] 网格尺寸
        * [x] 离散网格数量（nx）
    * [ ] 边界条件（bcs）
        * [x] Dirichlet BC 小孔边界
        * [x] Dirichlet BC sine-wave边界
        * [x] Neumann BC
    * [ ] 组件特征
        * [ ] 组件类型
            * [x] rectangle
            * [x] circle
            * [x] capsule
            * [ ] triangle
        * [ ] 组件大小（units）
            * [x] 长
            * [x] 宽
        * [ ] 功率（powers）
            * [x] 固定值
            * [x] 多选一
            * [x] uniform采样
        * [ ] 功率类型
            * [x] 固定功率
            * [x] 高斯分布功率
        * [ ] 组件位置和角度
            * [x] 组件中心位置坐标（positions）
            * [x] 组件放置角度（angles）
        * [x] 组件数量
    * [ ] 存储格式
        * [x] mat格式
    * [ ] 测点选取策略
        * [x] random
        * [x] uniform
        * [x] center

## 安装方式

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

## 快速入门 (Easy Starting)

* `data generate`执行如下命令

```python
recon-data-generator generate
```

* `plot`执行如下命令

```
recon-data-generator plot
```

