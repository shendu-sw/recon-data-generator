# -*- encoding: utf-8 -*-
"""
Desc      :   command line interface entry.
"""
# File    :   cli.py
# Time    :   2021/07/15 21:59:45
# Author  :   Zhiqiang Gong
# Contact :   gongzhiqiang13@nudt.edu.cn


import os
from pathlib import Path
from configargparse import ArgumentParser
from .config.configarg import get_parser_continuous_power
from .plot.plot import get_parser as get_plot_parser
from .version.about import __version__


def handle_generate(options):
    from .generator.generator import generate_from_cli

    preprocess(options.parser, options)
    generate_from_cli(options)
    options.nx += 1


def handle_plot(options):
    from .plot.plot import plot_dir, plot_mat

    if not options.dir:
        plot_mat(
            options.path,
            plot=options.plot_off,
            save=options.output,
            worker=options.worker,
        )  # single file
    else:
        plot_dir(options.path, out=options.output, worker=options.worker)


def preprocess(parser, options):
    if options.data_dir is not None:
        if not os.path.isdir(options.data_dir):
            os.mkdir(options.data_dir)
        # write config.yml in data_dir
        config_file_data = options.data_dir + "/config.yml"
        parser.write_config_file(options, [config_file_data])
        # cli 中 nx 为节点数，fenics求解过程中为单元数
        options.nx -= 1
        del_parser(options)  # fix error for multiprocessing


def del_parser(options):
    if hasattr(options, "parser"):
        del options.parser


def main(debug=False, options_flag=False):
    parser = ArgumentParser()
    parser.add(
        "-V",
        "--version",
        action="version",
        version=f"recon-data-generator version: {__version__}",
    )
    subparsers = parser.add_subparsers(title="commands")

    generate_parser = subparsers.add_parser(
        "generate", help="generate layout data with different power sampling"
    )
    generate_parser = get_parser_continuous_power(generate_parser)
    generate_parser.set_defaults(
        handle=handle_generate, parser=generate_parser
    )

    plot_parser = subparsers.add_parser("plot", help="plot layout data")
    plot_parser = get_plot_parser(plot_parser)
    plot_parser.set_defaults(handle=handle_plot)

    options, _ = parser.parse_known_args()

    if hasattr(options, "test") and options.test:  # 仅测试，输出参数
        print(parser.format_values())
        print(options)
        # print(sys.argv)
        parser.exit()

    if debug:
        del_parser(options)
        return parser, options

    if hasattr(options, "handle"):
        options.handle(options)

    if options_flag:
        return options


if __name__ == "__main__":
    main()