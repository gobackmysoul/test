#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  network.py
#    @Author        :  搏鲨
#    @Create date   :  18-9-20 下午9:55
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""
 搏鲨斗地主服务器
"""
import json
from multiprocessing import Process
from random import shuffle, sample
from socket import *
from signal import *
import sys
import os
import time
from threading import Thread


class User(object):
    """
    用户类
    """

    def __init__(self, name, host, port, money):
        # 用户名
        self.name = name
        # 用户host
        self.host = host
        # 用户端口
        self.port = port
        # 用户余额
        self.money = money
        # 游戏端口
        self.game_port = 4444
        # 抢地主的分数
        self.score = 0
        # 是否是地主
        self.is_win = False
        # 看是否抢过地主
        self.qiang = False


class Room(object):
    """
    房间类,用户创建的房间的实体
    """

    def __init__(self, name, uname, host, port):
        # 房主名字
        self.homeowner = uname
        # 初始化房间名
        self.name = name
        # 初始化房间成员列表, 把房主添加到房间成员
        user = User(uname, host, port, 0)
        # 房主第一把优先抢两次
        user.times = 2
        self.member = [user]

    def append(self, member):
        """
        添加房间成员
        """
        # 只有房间人数小于三人时才能加入房间
        if len(self.member) < 3:
            self.member.append(member)
            return True
        else:
            return False

    def remove(self, member):
        """
        移除房间成员
        """
        # 只有房间内人数>0 时才能删除成员
        if len(self.member) > 0:
            self.remove(member)
            return True
        else:
            return False


class Server(object):
    """
    服务类
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        # 创建数据报套接字
        self.sockfd = socket(AF_INET, SOCK_DGRAM)
        # 设置端口可重用
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # 绑定端口
        self.sockfd.bind((self.host, self.port))
        # 登录的玩家
        self.login_user = []
        # 房间列表
        self.room = []
        self.rob = 4
        # 倍数
        self.bei = 15

    def get_game_addr(self):
        """
        获取与用户交互的套接字地址
        """
        # 读取配置文件获取端口号和主机地址
        with open('/mnt/hgfs/share/untitled/斗地主/config/play_config.txt', 'r') as f:
            data = f.read()
            new_data = json.loads(data)
            host = new_data['host']
            port = new_data['port']
        return (host, port)

    def make_card(self):
        """
        生产牌
        """
        # 初始化牌容器
        cards = ['dw2000', 'xw1000']
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
        # 打乱牌的顺序
        shuffle(cards)
        return cards

    def do_play(self, rooms, room):
        """
        处理游戏主要逻辑
        """
        ready_user = []
        print("主进程中的列表id：", id(ready_user))
        # 重新创建新的套接字负责处理游戏主逻辑
        # 获取游戏套接字地址
        addr = self.get_game_addr()
        sockfd = socket(AF_INET, SOCK_DGRAM)
        sockfd.bind(addr)
        # 接受三个人游戏的套接字端口改变请求
        for i in range(3):
            data, addr = sockfd.recvfrom(1024)
            data = data.decode().split(":")
            print("接收到改变port请求")
            if data[0] == 'change_port':
                for user in room.member:
                    if user.name == data[1]:
                        # 改变她得port
                        user.game_port = addr[1]
                        print("改变之后的端口: {}".format(addr[1]))
        # 发送可以准备的标志
        for user in room.member:
            data = "{}:".format('start')
            sockfd.sendto(data.encode(), (user.host, user.game_port))
            print("能开始游戏信息发送完毕")
        # 先判断3个人是否都准备
        while True:
            data, addr = sockfd.recvfrom(1024)
            data = data.decode().split(":")
            if data[0] == 'ready':
                print("有人准备了")
                for i in room.member:
                    if i.name == data[1]:
                        i.game_port = addr[1]
                        # 把准备的用户添加到准备列表中
                        ready_user.append(i)
                        break
                if len(ready_user) == 3:
                    break
        print("游戏正式开始发牌中")
        cards = self.make_card()
        # 给每个玩家发牌
        for i in ready_user:
            addr = (i.host, i.game_port)
            # 从中随机抽取１７张牌
            send_card = sample(cards, 17)
            # 从牌中把抽取的牌去掉
            for j in send_card:
                if j in cards:
                    cards.remove(j)
            card = ':'.join(send_card)
            data = "{}:{}".format('send_cards', card)
            sockfd.sendto(data.encode(), addr)
        # 给每个玩家发送自己位置
        for index, user in enumerate(room.member, start=1):
            data = '{}:{}'.format('order', index)
            sockfd.sendto(data.encode(), (user.host, user.game_port))
        print("发送位置完毕")
        # 给每个玩家发送能抢地主的信息
        for user in room.member:
            data = '{}:'.format('qiang')
            sockfd.sendto(data.encode(), (user.host, user.game_port))
            print("向{}发送了能请地主消息".format(user.game_port))
            # 接受用户抢地主消息
            rec_data, addr = sockfd.recvfrom(1024)
            rec_data = rec_data.decode().split(":")
            if rec_data[0] == 'qiang':
                # 如果用户点击了抢地主那么让他的分数+1
                if rec_data[1] == 'q':
                    user.score += 1
                    user.qiang = True
                    self.bei *= 2
                else:
                    user.score = 0
        # 判断分数大小,来得到地主
        scores = []
        for user in room.member:
            scores.append(user.score)
        max_score = max(scores)
        # 如果在第一轮没有分出谁是地主那么进行第二轮
        if scores.count(max_score) > 1:
            for user in room.member:
                if user.score > 0 and user.qiang:
                    data = '{}:'.format('qiang')
                    sockfd.sendto(data.encode(), (user.host, user.game_port))
                    rec_data, addr = sockfd.recvfrom(1024)
                    rec_data = rec_data.decode().split(":")
                    if rec_data[0] == 'qiang':
                        # 如果用户点击了抢地主那么让他的分数+1
                        if rec_data[1] == 'q':
                            user.score += 1
                            max_score = user.score
                            self.bei *= 2
                            break
                        else:
                            # 如果不抢则让下一个抢
                            user.qiang = False
                            user.score -= 1
                            continue
        for user in room.member:
            # 判断是否是该用户最终抢到地主
            if user.score == max_score:
                dizhu_position = room.member.index(user)
                user.is_win = True
                print(user.name + "是地主")
                win_data = "{}:{}:{}:{}".format('win', user.name, room.member.index(user) + 1, self.bei)
        # 新的用户位置
        if dizhu_position == 0:
            new_user_position = room.member
        elif dizhu_position == 1:
            new_user_position = [room.member[1], room.member[2], room.member[0]]
        elif dizhu_position == 2:
            new_user_position = [room.member[2], room.member[0], room.member[1]]
        for user in room.member:
            # 向客户端发送谁是地主的消息
            sockfd.sendto(win_data.encode(), (user.host, user.game_port))
        # 发送底牌
        for user in room.member:
            data = '{}:{}:{}:{}'.format('di', cards[0], cards[1], cards[2])
            sockfd.sendto(data.encode(), (user.host, user.game_port))
        # 发送出牌标志位
        while True:
            for user in new_user_position:
                send_data = 'is_send:'
                sockfd.sendto(send_data.encode(), (user.host, user.game_port))
                rec_data, addr = sockfd.recvfrom(1024)
                for i in new_user_position:
                    if i != user:
                        sockfd.sendto(rec_data, (i.host, i.game_port))
                # 判断该牌是否为给用户最后一张牌
                if rec_data.decode().split(":")[-1] == '0':
                    # 结束时初始化倍数
                    self.bei = 15
                    if user.is_win:
                        js = "dizhu"
                    else:
                        js = "nong"
                    data = "end:{}".format(js)
                    # 发送输赢信息
                    for i in new_user_position:
                        if i != user:
                            print("发送输赢信息")
                            sockfd.sendto(data.encode(), (i.host, i.game_port))
                    os._exit(0)

    def run_server(self):
        while True:
            data, addr = self.sockfd.recvfrom(1024)
            print("{}:{}".format(addr, data.decode()))
            data = data.decode().split(":")
            # 登录请求处理
            if data[0] == 'login':
                try:
                    uname = data[1]
                    host = addr[0]
                    port = addr[1]
                    # 用户登录创建用户对象
                    user = User(uname, host, port, 0)
                    # 往在线用户列表中添加登录用户
                    self.login_user.append(user)
                except Exception as e:
                    print("login_error: ", e)
            # 创建房间请求处理
            elif data[0] == 'create':
                try:
                    print("创建房间请求")
                    # 获取用户创建房间的名称以及用户的信息
                    room_name = data[1]
                    # 验证房间是否重复
                    for room in self.room:
                        if room_name == room.name:
                            data = "{}:{}".format('create', 'exist')
                            # 往客户端发送房间名重复标志位
                            self.sockfd.sendto(data.encode(), addr)
                            break
                    else:
                        uname = data[2]
                        host = addr[0]
                        port = addr[1]
                        # 创建房间对象
                        room = Room(room_name, uname, host, port)
                        print("房间成员个数", len(room.member))
                        # 往房间列表中添加房间对象
                        self.room.append(room)
                        print("房主地址:", port)
                        for i in self.login_user:
                            # 创建房间,往所有人发送创建房间信息,在客户端显示房间
                            print("成员地址: ", i.port)
                            data = "{}:{}:{}".format('create', 'success', room_name)
                            self.sockfd.sendto(data.encode(), (i.host, i.port))
                            print("发送消息完毕")
                        time.sleep(0.5)
                        # 给房主发送标志位让他进入游戏
                        data = "{}:{}".format("create", 'play')
                        self.sockfd.sendto(data.encode(), addr)
                        print(self.room[0].member[0].name)
                except Exception as e:
                    data = "{}:{}".format('create', 'fail')
                    # 发送房间创建成功标志位
                    self.sockfd.sendto(data.encode(), addr)
                    print("create_error: ", e)

            # 进入房间请求处理
            elif data[0] == 'into':
                try:
                    room_name = data[1]
                    uname = data[2]
                    host = addr[0]
                    port = addr[1]
                    # 创建用户对象
                    user = User(uname, host, port, 0)
                    for i in self.room:
                        # 遍历房间列, 把改用户添加到房间成员
                        if i.name == room_name:
                            is_succ = i.append(user)
                            # 判断是否进入成功
                            if is_succ:
                                print("进入成功")
                                print("人员个数", len(i.member))
                                # 进入成功之后往客户端返回标志位
                                data = "{}:{}".format('room', 'success')
                                self.sockfd.sendto(data.encode(), addr)
                                # 如果房间里面有三个人就开启游戏
                                if len(i.member) == 3:
                                    print("开启游戏")
                                    p = Thread(target=self.do_play, args=(self.room, i))
                                    p.daemon = True
                                    p.start()
                            else:
                                # 如果房间已满则返回full标志位
                                data = "{}:{}".format('room', 'full')
                                self.sockfd.sendto(data.encode(), addr)

                except Exception as e:
                    print("into_error: ", e)
            # 离开房间请求
            elif data[0] == 'quit':
                pass


def get_addr(file):
    """
    获取地址
    """
    # 读取配置文件获取端口号和主机地址
    with open(file, 'r') as f:
        data = f.read()
        new_data = json.loads(data)
        host = new_data['host']
        port = new_data['port']
    return (host, port)


def main():
    """
    主逻辑调用函数
    """
    # 处理僵尸进程
    signal(SIGCHLD, SIG_IGN)
    addr = get_addr('server_config.txt')
    server = Server(*addr)
    server.run_server()


if __name__ == '__main__':
    main()
