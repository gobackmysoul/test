#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  client.py
#    @Author        :  搏鲨
#    @Create date   :  18-9-22 上午9:27
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""
 
"""
from socket import *
import sys
import json

# 读取配置文件获取端口号和主机地址
with open('/mnt/hgfs/share/untitled/斗地主/network/play_config.txt', 'w') as f:
    data = {'host': '127.0.0.1', 'port': 3333}
    new_data = json.dumps(data)
    f.write(new_data)

# client_sockfd.bind(client_addr)
