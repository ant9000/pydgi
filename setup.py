#!/usr/bin/env python3

import setuptools

setuptools.setup(
    name='pydgi',
    version='0.1.5',
    author="Antonio Galea",
    author_email="antonio.galea@gmail.com",
    description="Python implementation for Microchip/Atmel Data Gateway Interface",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ant9000/pydgi",
    packages=setuptools.find_packages(),
    package_data={'dgi': ['docs/*.pdf', 'examples/*py']},
    scripts=['dgi_power_measure.py'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    install_requires=["pyusb>=1"],
)
