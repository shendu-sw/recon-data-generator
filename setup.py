import os
import pathlib
from setuptools import setup, find_packages
import src.version.about as about


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")


def load_requirements(path_dir=here, comment_char="#"):
    with open(os.path.join(path_dir, "requirements.txt"), "r") as file:
        lines = [line.strip() for line in file.readlines()]
    requirements = []
    for line in lines:
        # filer all comments
        if comment_char in line:
            line = line[: line.index(comment_char)]
        if line:  # if requirement is not empty
            requirements.append(line)
    return requirements


setup(
    name="recon-data-generator",
    version=about.__version__,
    author=about.__author__,
    author_email="gongzhiqiang13@nudt.edu.cn",
    url="http://github.com/shendu-sw/recon-data-generator",
    license=about.__licence__,
    description=about.__desp__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=load_requirements(),
    
    include_package_data=True,
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["recon_data_generator = src.cli:main",]
    },
)
