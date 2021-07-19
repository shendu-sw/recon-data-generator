# -*- encoding: utf-8 -*-
"""
Desc      :   config based argparser.
"""
# File    :   configarg.py
# Time    :   2021/07/09 08:33:57
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn

import os
import shutil
import configargparse
from pathlib import Path
import yaml
import numpy as np

from src.version.about import __version__


here = Path(__file__).resolve().parent


def get_parser_common(parser: configargparse.ArgumentParser, config_name: str):
    config_path = here / config_name
    assert config_path.exists(), "Config do not exist!"

    parser._config_file_parser = configargparse.YAMLConfigFileParser()
    parser._default_config_files = [str(config_path)]

    parser.add("--config", is_config_file=True, help="config file path")
    parser.add("--test", action="store_true", help="test mode")
    parser.add("--length", type=float, help="board length")
    parser.add("--length_unit", type=float, help="unit length")
    parser.add(
        "--bcs",
        type=yaml.safe_load,
        action="append",
        help="Dirichlet boundaries",
    )

    parser.add(
        "--data_dir", type=str, help="dir to store generated layout data"
    )

    parser.add("--fem_degree", type=int, help="fem degree in fenics")
    parser.add("--u_D", type=int, help="value on Dirichlet boundary")
    parser.add("--nx", type=int, help="number of grid in x direction")

    parser.add("--sample_n", type=int, help="number of samples")
    parser.add(
        "--seed",
        type=int,
        default=np.random.randint(2 ** 32),
        help="seed in np.random module",
    )
    parser.add(
        "--file_format", type=str, choices=["mat"], help="dataset file format"
    )
    parser.add("--prefix", type=str, help="prefix of file")
    parser.add(
        "--method",
        type=str,
        choices=["fenics"],
        help="method to solve the equation",
    )
    parser.add(
        "--worker", type=int, default=os.cpu_count(), help="number of workers"
    )
    parser.add("--ndim", type=int, choices=[2, 3], help="dimension")
    parser.add(
        "--vtk", action="store_true", default=False, help="output vtk file"
    )
    parser.add(
        "-V",
        "--version",
        action="version",
        version=f"layout-generator version: {__version__}",
    )
    parser.add(
        "--task", help="task", choices=["discrete", "continuous"], type=str
    )
    return parser


def get_parser_continuous_power(
    parser: configargparse.ArgumentParser, config_path=None
):
    parser = get_parser_common(parser, "default_c_power.yml")

    parser.add(
        "--units",
        action="append",
        type=yaml.safe_load,
        help="shape of each unit",
    )
    parser.add(
        "--angles",
        action="append",
        type=float,
        help="angle of each unit",
    )
    parser.add(
        "--powers",
        action="append",
        type=yaml.safe_load,
        help="power of each unit",
    )
    parser.add(
        "--power_distribution",
        action="append",
        type=yaml.safe_load,
        help="power distribution of each unit",
    )
    parser.add("--gaussian_param", type=float, help="parameter in gaussian power distribution.")
    parser.add(
        "--geometry",
        action="append",
        type=yaml.safe_load,
        help="shape of each unit: rectangle, circle, capsule",
    )
    parser.add(
        "--positions",
        action="append",
        type=yaml.safe_load,
        help="positions of each unit",
    )
    parser.add(
        "--positions_type",
        type=str,
        choices=['coord', 'grid'],
        help="the type of input positions: coord or grid",
    )
    parser.add(
        "--special",
        type=type, 
        default='off',
        help="generate special samples or not",
    )
    parser.add(
        "--special_num",
        type=int,
        default=0,
        help="number of special heat source (zero power intensity)",
    )
    parser.add(
        "--monitoring_sampling",
        action="append",
        type=yaml.safe_load,
        help="Sampling monitoring points",
    )

    return parser
