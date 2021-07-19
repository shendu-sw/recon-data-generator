# Data Generator for Temperature Field Reconstruction of Heat Source Systems

> This project is based on [FEniCS](https://fenicsproject.org) and used for data generation of temperature field reconstruction samples.

## 功能支持（Support functions）
* 可配置选项
    * [ ] 布局板尺寸
        * [x] 长（length）
        * [x] 宽（width）
    * [ ] 边界条件
        * [x] Dirichlet BC 小孔边界
        * [x] Dirichlet BC sine-wave边界
        * [x] Neumann BC
    * [ ] 组件特征
        * [ ] 组件类型
            * [x] rectangle
            * [x] circle
            * [x] capsule
            * [ ] triangle
        * [ ] 组件大小
            * [x] 长
            * [x] 宽
        * [ ] 功率类型
            * [x] 固定功率
            * [x] 高斯分布功率
        * [ ] 组件位置和角度
            * [x] 组件中心位置坐标
            * [x] 组件放置角度
        * [x] 组件数量
    * [ ] 存储格式
        * [x] mat格式



## 快速入门 (Easy Starting)

* 安装同layout-generator数据生成器
* `data generate`执行如下命令

```python
recon-data-generator generate
```

* `plot`执行如下命令

```
recon-data-generator plot
```

