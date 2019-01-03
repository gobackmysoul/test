#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  cl.py
#    @Author        :  搏鲨
#    @Create date   :  18-9-22 上午10:27
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""
 
"""
import sys
# from client import client_sockfd
# client_sockfd.sendto(b'456', ('127.0.0.1', 8888))
from socket import *

sockfd = socket(AF_INET, SOCK_DGRAM)
sockfd.connect(('8.8.8.8', 80))
ip = sockfd.getsockname()[0]
print(type(ip))