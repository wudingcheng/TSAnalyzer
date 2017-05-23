#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys
import os
from qtpy.QtCore import PYQT_VERSION_STR

PY2 = sys.version[0] == '2'
PY3 = sys.version[0] == '3'
pyqt_version = float(PYQT_VERSION_STR[:3])

python_version = 'py2' if PY2 else 'py3'
pyrcc_compiler = 'pyrcc4' if pyqt_version < 5 else 'pyrcc5'

# compile resource file
QRC_DIR = "TSAnalyzer/TSResource"
os.system(
    '{} -o {}/images.py {}/images.qrc'
    .format(pyrcc_compiler, QRC_DIR, QRC_DIR)
)

# compilt ui file
UI_DIR = "TSAnalyzer/TSWidgets"
uic_compiler = 'pyuic4' if pyqt_version < 5 else 'pyuic5'
os.system("{} -o {}/MainWindow.py {}/main.ui"
          .format(uic_compiler, UI_DIR, UI_DIR))
os.system("{} -o {}/AboutDialog.py {}/about.ui"
          .format(uic_compiler, UI_DIR, UI_DIR))
os.system("{} -o {}/AnalysisBatchDialog.py {}/analysis_batch.ui"
          .format(uic_compiler, UI_DIR, UI_DIR))
os.system("{} -o {}/FigureBatchDialog.py {}/figure_batch.ui"
          .format(uic_compiler, UI_DIR, UI_DIR))
os.system("{} -o {}/HeaderDialog.py {}/header.ui"
          .format(uic_compiler, UI_DIR, UI_DIR))
os.system("{} -o {}/OffsetDialog.py {}/offset.ui"
          .format(uic_compiler, UI_DIR, UI_DIR))
os.system("{} -o {}/LogDialog.py {}/log.ui"
          .format(uic_compiler, UI_DIR, UI_DIR))
os.system("{} -o {}/SigsegDialog.py {}/sigseg.ui"
          .format(uic_compiler, UI_DIR, UI_DIR))
os.system("{} -o {}/DateDialog.py {}/date.ui"
          .format(uic_compiler, UI_DIR, UI_DIR))

# sig = subprocess.Popen(["gcc", "-fPIC", "-shared",
#                         "TSAnalyzer/TSModel/sigseg/libseg1d.c",
#                         "-o",
#                         "TSAnalyzer/TSModel/sigseg/libseg1d.so"]).wait()

setup(
    name='TSAnalyzer',
    version='1.2',
    description='Python GNSS Time Series Analysis and Visualaztion',
    license='GPL v3',
    author='wudingcheng',
    author_email='wudingcheng14@mails.ucas.ac.cn',
    packages=find_packages(),
    package_data={'TSAnalyzer': ['*.pyw',
                                 'TSModel/sigseg/*',
                                 'TSWidgets/*.ui',
                                 'TSResource/*',
                                 'TSResource/images/*']},
    install_requires=['matplotlib>=1.1',
                      'pandas>=0.17',
                      'numpy',
                      'qtpy'],
    zip_safe=False,
    entry_points={'gui_scripts': [
        'TSAnalyzer = TSAnalyzer:main']}
)
