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


# import sys
# from client import client_sockfd
# client_sockfd.sendto(b'456', ('127.0.0.1', 8888))
from random import *
def make_card():
    # 初始化牌容器
    cards = ['dw', 'xw']
    for i in range(4):
        if i == 0:
            hua = 'ht'
        elif i == 1:
            hua = 'hx'
        elif i == 2:
            hua = 'fp'
        elif i == 3:
            hua = 'mh'
        for j in range(3, 16):
            card = hua + str(j)
            cards.append(card)
    shuffle(cards)
    card = sample(cards, 17)
    card = ':'.join(card)
    data = "{}:{}".format('send_card', card)
    print(data)
make_card()
