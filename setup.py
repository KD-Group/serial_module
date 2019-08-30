#!/usr/bin/env python
# -*- coding: utf-8 -*-
# comment: 部署所需信息, pypi上显示的内容
"""
:copyright: (c) 2018 by Jefung
"""
import os
from setuptools import setup
import subprocess


def get_git_latest_tag():
    def _minimal_ext_cmd(cmd: str):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd("git describe --abbrev=0 --tags")
        git_tag = out.strip().decode('ascii')
    except OSError:
        git_tag = None

    return git_tag


latest_tag = get_git_latest_tag()
if latest_tag is None:
    print("get_git_latest_tag return None")
    exit(1)

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


print("use latest tag as version: {}".format(latest_tag))
print("use requirements.txt as install_requires: {}".format(req_list))

setup(
    name="serial_module",
    version=latest_tag,
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
    packages=["serial_module"],
    install_requires=req_list,
    python_requires='>=3',
)
