#!/usr/bin/env python
# -*- coding: utf-8 -*-
# comment: 部署所需信息, pypi上显示的内容
"""
:copyright: (c) 2018 by Jefung
"""
import os
import sys
from setuptools import setup
from setuptools.command.install import install
import subprocess

# 要部署, 必须设置当前分支的git tag和VERSION一样.
VERSION = "1.0.1"


# 流程:
# 1. 修改VENSION: VERSION = "1.0.1"
# 2. git提交: git_hooks add setup.py && git_hooks commit -m "upload pypi" && git_hooks push
# 3. 增加tag: git_hooks tag -a [版本号] -m "说明文字"
# 4. 提交tag: git_hooks push --tag   // origin可修改为你的其它分支

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
        out = _minimal_ext_cmd("git_hooks describe --abbrev=0 --tags")
        git_tag = out.strip().decode('ascii')
    except OSError:
        git_tag = "Unknown"

    return git_tag


def readme():
    """读取README.md文件"""
    with open('README-en.md', encoding="utf-8") as f:
        return f.read()


class VerifyVersionCommand(install):
    """确定当前分支的最新tag是否和VERSION变量一致,不一致则报错"""
    description = 'verify that the git_hooks tag matches our version'

    def run(self):
        git_latest_tag = get_git_latest_tag()
        if git_latest_tag != VERSION:
            info = "Git tag: {0} does not match the version of this project: {1}".format(git_latest_tag, VERSION)
            sys.exit(info)


setup(
    name="serial module",
    version=VERSION,
    description="串行接口模块简单包装,支持模拟接口和真实接口",
    long_description=readme(),
    author="Jefung",
    author_email="865424525@qq.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    keywords='python serial',
    packages=[],
    install_requires=[
        'serial',
    ],
    python_requires='>=3',
    cmdclass={
        # python setup.py verify 调用VerifyVersionCommand
        'verify': VerifyVersionCommand,
    }
)
