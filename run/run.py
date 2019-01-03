#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  run.py
#    @Author        :  搏鲨
#    @Create date   :  18-9-22 下午1:35
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""
 游戏运行主模块
"""
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from login import login


def main():
    login.main()


if __name__ == '__main__':
    main()
