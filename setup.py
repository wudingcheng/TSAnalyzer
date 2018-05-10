#!/usr/bin/env python
# author: WU Dingcheng
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='TSAnalyzer',
    version='1.3',
    description='Python GNSS Time Series Analysis and Visualization',
    license='GPL v3',
    author='WU Dingcheng',
    author_email='wudingcheng14@mails.ucas.ac.cn',
    url='https://github.com/wudingcheng/tsanalyzer',
    packages=find_packages(),
    package_data={'TSAnalyzer': ['resources/style.qss',
                                 'resources/images/*',
                                 'resources/ui/*.ui']},
    install_requires=[
        'matplotlib',
        'pandas',
        'numpy',
        'qtpy',
        'cvxpy'],
    entry_points={'gui_scripts': ['TSAnalyzer = TSAnalyzer:main']}
)
