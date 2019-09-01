#!/usr/bin/env python
# -*- coding: utf-8 -*-
# comment: 部署所需信息, pypi上显示的内容
"""
:copyright: (c) 2018 by Jefung
"""
import os
from setuptools import setup, find_packages
import subprocess
from version import get_git_version

# 读取项目下的requirements.txt
req_txt_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(req_txt_path):
    with open(req_txt_path) as f:
        req_list = f.readlines()
    req_list = [x.strip() for x in req_list]
else:
    req_list = []


def readme():
    """读取README.md文件"""
    with open('README.md', encoding="utf-8") as f:
        return f.read()


print("use latest tag as version: {}".format(get_git_version()))
print("use requirements.txt as install_requires: {}".format(req_list))

setup(
    name="serial_module",
    version=get_git_version(),
    url="https://github.com/KD-Group/serial_module",
    description="串行接口模块简单包装,支持模拟接口和真实接口",
    long_description=readme(),
    long_description_content_type='text/markdown',
    author="Jefung",
    author_email="865424525@qq.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    keywords='python serial',
    packages=find_packages(exclude=['docs', 'tests', 'examples']),
    # packages=["serial_module"],
    install_requires=req_list,
    python_requires='>=3',
)
