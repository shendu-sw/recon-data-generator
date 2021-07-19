"""main function.

"""
# File    :   main.py
# Time    :   2021/07/09 08:33:57
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn

import os
from pathlib import Path
from configargparse import ArgumentParser

from .config.configarg import get_parser_continuous_power, get_parser_makeconfig, makeconfig
from .generator import solver
from .generator.generator import generate_from_cli
from .version.about import __version__


if __name__ == '__main__':

    parser = ArgumentParser()
    parser = get_parser_continuous_power(parser)
    hparams = parser.parse_args()
    generate_from_cli(hparams)
