#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  play.py
#    @Author        :  搏鲨
#    @Create date   :  18-9-16 下午8:41
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""
搏鲨斗地主游戏界面
"""
import json
import sys
from multiprocessing import Process
from threading import Thread

"""
2018 9/19 0:27 
问题
   1.  当点击出牌时牌的上下移动失效
           9 /19 23:21 解:
                出牌了但是并没有把列表里的牌删除,导致寻找牌设置位置失效
                
                
　　2.　剩余牌自动刷新位置并显示在相应位置.
           9 /19 23:21 解:
            没有清空原来列表的位置，上次的数据依然在列表里,导致数据重复，盖压原来的牌，导致位置不能刷新
            
            
2018  9/25 23 : 49
问题            
    当为三个人创建独立的处理进程处理相关逻辑时,用到的套接字应该更换端口,并且客户端也应该获得,
    客户端更新套接字端口, 先给服务器发送准备消息，服务器获取当前客户端的游戏端口, 当客户端知道
    服务器的游戏端口,服务器知道客户端的游戏接口，这是就可以通信了
"""
from socket import *
import pygame
import time
import pygame.mouse
import copy
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from models import MySQL


class Play(object):
    """
    游戏类
    """

    def __init__(self):
        self.select_cards_show = False
        self.kaishi = False
        self.shang = False
        # 总牌
        self.cards = []
        # 底牌
        self.di = []
        # 选中的牌
        self.select_cards = []
        # 发送的牌
        self.hidden_card = []
        # 　牌具体信息
        self.card_position = []
        # 是否接收到了牌
        self.is_have_card = False
        # 发送的牌起始位置的X值
        self.send_card_showx = 600
        self.send_card_showy = 350
        self.card_path = '../images/pai/'
        # 是否刷新牌的位置
        self.flush_position = False
        # 自己的位置
        self.order = 0
        # 赢标志位
        self.is_win = False
        # 能出牌的标志位
        self.is_send = False
        # 是否能抢地主的标志位
        self.is_qiang = False
        # 匹配玩家
        self.pipei = True
        # 是否是地主
        self.is_dizhu = False
        # 是否是农民
        self.is_nong = False
        # 上家的名字
        self.history_name = ''
        # 上家发送牌的值
        self.value = 0
        # 上家发送牌的值
        self.card_num = 0
        # 上家发送的牌
        self.history_card = []
        # 是否显示上家出的牌
        self.show_history = False
        # 是否显示不符合规则
        self.guize = False
        # 输赢身份标志
        self.dizhu_win = False
        self.dizhu_fail = False
        self.nong_win = False
        self.nong_fail = False

        # 倍数
        self.bei = 15
        # 最低钱数
        self.money = 10

    def do_sql(self, sql):
        """
        操作数据库接口
        """
        db = MySQL.MySQL('localhost', 3306, 'root', '123456', 'doudizhu', 'utf8')
        db.getdatabase()
        data = db.start(sql)
        return data

    def set_money(self, uname):
        """
        获取用户余额
        """
        if self.is_win:
            if self.is_dizhu:
                self.money = self.money * self.bei * 2
            else:
                self.money *= self.bei
        else:
            if self.is_dizhu:
                self.money = -(self.money * self.bei * 2)
            else:
                self.money *= -(self.bei)
        print("钱", self.money)
        sql = "update user set money=money+{} where username='{}';".format(self.money, uname)
        data = self.do_sql(sql)
        # 初始化输赢标志
        self.is_win = False

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

    def get_card_value(self, cards):
        def get_value(card):
            """
            获取牌的值
            """
            dian_index = card.find('.')
            value = int(card[2:dian_index])
            return value

        values = []
        # 获取出的牌的值
        for i in cards:
            values.append(get_value(i))
        # 炸牌值获取规则
        if values.count(values[0]) == 4:
            return values[0] ** 4 * 10
        # 王炸牌获取规则
        if 1000 in values and 2000 in values:
            return values[0] * values[1]
        return sum(values)

    def send_recv(self, sockfd, uname):
        """
        与服务器数据交互
        """
        while True:
            data, addr = sockfd.recvfrom(1024)
            data = data.decode().split(":")
            if data[0] == 'send_cards':
                c = data[1:]
                cards = []
                #  生成对应牌的名字
                for i in c:
                    i = i + '.png'
                    cards.append(i)
                self.cards = sorted(cards, key=self.card_sort, reverse=True)
                self.set_card_position()
                self.is_have_card = True
            elif data[0] == 'order':
                # 设置自己的顺序
                self.order = data[1]
            elif data[0] == 'qiang':
                self.is_qiang = True
            elif data[0] == 'start':
                # print("能进入游戏了")
                self.kaishi = True
            elif data[0] == 'win':
                print("翻倍了", data[3])
                self.bei = int(data[3])
                if data[1] == uname:
                    self.is_dizhu = True
                else:
                    self.is_nong = True
            elif data[0] == 'di':
                if self.is_dizhu:
                    for i in range(1, 4):
                        # print(data[i])
                        self.cards.append(data[i] + ".png")
                        # 给加上底牌的牌的牌排序
                        self.cards = sorted(self.cards, key=self.card_sort, reverse=True)
                        # print("牌总数", len(self.cards))
                        self.di.append(data[i])
                        # 刷新牌
                        self.flush_position = True
                else:
                    for i in range(1, 4):
                        self.di.append(data[i])
            elif data[0] == 'is_send':
                self.is_send = True

            elif data[0] == 'send_card':
                if data[1] != 'pass':
                    self.show_history = True
                    # 不显示自己出的牌
                    self.select_cards_show = False
                    cards = data[2:len(data) - 1]
                    # 如果上家的牌为炸,则翻倍
                    if self.is_zha(cards):
                        self.bei *= 2
                        print("上家牌为炸翻倍")
                    # print("上家出的牌", data[2:])
                    self.card_num = len(cards)
                    self.value = self.get_card_value(cards)
                    self.history_card = cards
                    # 设置上次出牌人的姓名
                    self.history_name = data[1]

            elif data[0] == 'end':
                print("接收到了输赢消息!")
                win = data[1]
                # 地主赢了
                if win == 'dizhu':
                    self.nong_fail = True
                    # 如果自己是地主则判断输赢
                    if self.is_dizhu:
                        self.is_win = True
                    else:
                        self.is_win = False
                # 农民赢了
                elif win == 'nong':
                    # 如果自己是农民自己也赢了
                    if self.is_nong:
                        self.nong_win = True
                        self.is_win = True
                    # 如果自己是地主那么自己输了
                    elif self.is_dizhu:
                        self.dizhu_fail = True
                        self.is_win = False
                # 结算钱
                self.set_money(uname)
                print("结束啦")

    def draw_fanmian(self, fanmian):
        for i in range(200, 501, 50):
            self.top.blit(fanmian, (i, 250))
        for i in range(1000, 1300, 50):
            self.top.blit(fanmian, (i, 250))

    def rule(self):
        def get_value(card):
            """
            获取牌的值
            """
            dian_index = card.find('.')
            value = int(card[2:dian_index])
            return value

        # 是否为单牌
        def is_dan():
            if len(self.select_cards) == 1:
                print("是单牌")
                return True
            else:
                return False

        # 是否为对牌
        def is_dui():
            # position = [i, x, 650, False]
            if len(self.select_cards) == 2 and get_value(self.select_cards[0][0]) == get_value(self.select_cards[1][0]):
                print("是对牌")
                return True
            else:
                return False

        # 是否为顺子
        def is_shun():

            if len(self.select_cards) >= 5:
                is_shun = True
                # 是否包含2
                for i in self.select_cards:
                    if get_value(i[0]) > 14:
                        print("顺子包含2不符合规则")
                        return False
                for i in range(0, len(self.select_cards) - 1):
                    if get_value(self.select_cards[i + 1][0]) - get_value(self.select_cards[i][0]) != 1:
                        print("差值不一样")
                        is_shun = False
                        break
                if is_shun:
                    print("是顺子")
                return is_shun
            else:
                return False

        # 是否为连对
        def is_liandui():
            is_liandui = True
            values = []
            for i in self.select_cards:
                values.append(get_value(i[0]))
            if 15 not in values:
                if len(self.select_cards) > 4 and (len(self.select_cards) % 2 == 0):
                    max = len(self.select_cards) - 1
                    for i in range(0, max, 2):
                        if get_value(self.select_cards[i][0]) != get_value(self.select_cards[i + 1][0]):
                            print("前后值不一样")
                            return False
                        if i < len(self.select_cards) - 2:
                            if get_value(self.select_cards[i][0]) - get_value(self.select_cards[i + 2][0]) != -1:
                                print("前后值差值不符合")
                                return False
                    if is_liandui:
                        print("是连对")
                    return is_liandui
                else:
                    print("不是二连以上或者不是偶数牌")
                    return False
            else:
                print("2在连队中")
                return False

        # 是否为三张牌
        def is_sanzhang():
            if len(self.select_cards) == 3:
                values = []
                for i in self.select_cards:
                    values.append(get_value(i[0]))
                # 判断牌的值出现的次数
                if values.count(values[0]) == 3:
                    print("是三张牌")
                    return True

                else:
                    return False
            else:
                return False

        # 是否为三带一
        def is_sandaiyi():
            is_sandaiyi = False
            if len(self.select_cards) == 4:
                values = []
                for i in self.select_cards:
                    values.append(get_value(i[0]))
                # 判断牌的值出现的次数
                for i in values:
                    if values.count(i) == 3:
                        print("是三带一")
                        is_sandaiyi = True
                        break
                return is_sandaiyi
            else:
                return False

        # 是否为三带二
        def is_sandaier():
            is_have_three = False
            is_have_two = False
            if len(self.select_cards) == 5:
                values = []
                for i in self.select_cards:
                    values.append(get_value(i[0]))
                # 判断牌的值出现的次数
                for i in values:
                    # 三张牌
                    if values.count(i) == 3:
                        is_have_three = True
                    # 对牌
                    elif values.count(i) == 2:
                        is_have_two = True
                if is_have_two and is_have_three:
                    print("是三带二")
                return is_have_two and is_have_three
            else:
                return False

        # 是否为炸
        def is_zha():
            if len(self.select_cards) == 4:
                values = []
                for i in self.select_cards:
                    values.append(get_value(i[0]))
                for i in values:
                    if values.count(i) == 4:
                        print("是炸")
                        return True
                    else:
                        return False
            else:
                # 是否为王炸
                if len(self.select_cards) == 2:
                    values = []
                    for i in self.select_cards:
                        values.append(get_value(i[0]))
                    if 2000 in values and 1000 in values:
                        print("是王炸")
                        return True
                return False

        # 是否为飞机
        def is_feiji():
            if len(self.select_cards) % 2 == 0:
                values = []
                for i in self.select_cards:
                    values.append(get_value(i[0]))
                # 判断是否有三张2
                if values.count(15) == 3:
                    return False
                else:
                    # 飞机连数
                    threes = []
                    # 带对数
                    twos = []
                    # 单牌数
                    ones = []
                    for i in values:
                        # 单牌
                        if values.count(i) == 1 or values.count(i) == 4:
                            if i not in ones:
                                ones.append(i)
                        # 对牌
                        if values.count(i) == 2 or values.count(i) == 4:
                            # 炸分开的对牌加入两次
                            if values.count(i) == 4 and i not in twos:
                                twos.append(i)
                                twos.append(i)
                            if i not in twos:
                                twos.append(i)
                            if i not in ones:
                                ones.append(i)
                                ones.append(i)
                        # 判断飞机连牌是否为3个重复的牌
                        if values.count(i) == 3 or (values.count(i) == 4 and i not in twos):
                            if i not in threes:
                                threes.append(i)

                    is_lian = True
                    # print('单牌', ones)
                    # print('对牌', twos)
                    # print('三张', threes)

                    if len(threes) > 1:
                        # 给连牌的牌排序
                        threes.sort()
                        for i in range(0, len(threes) - 1):
                            if threes[i + 1] - threes[i] != 1:
                                is_lian = False
                        # 连牌数和带牌数是否一致
                        is_eq = len(threes) == len(ones) or len(threes) == len(twos)
                        if is_lian and is_eq:
                            print("是飞机")
                        return is_lian and is_eq
            else:
                return False

        # 是否为4带2
        def is_sidaier():
            if len(self.select_cards) % 2 == 0:
                ones = []
                twos = []
                fours = []
                values = []
                for i in self.select_cards:
                    values.append(get_value(i[0]))
                for i in values:
                    if values.count(i) == 1 or values.count(i) == 2:
                        if i not in ones:
                            ones.append(i)
                    if values.count(i) == 2 or values.count(i) == 4:
                        if values.count(i) == 4 and i not in values:
                            twos.append(i)
                            twos.append(i)
                        # 牌没有出现在对牌列表里
                        if i not in twos:
                            twos.append(i)
                    if values.count(i) == 4 and i not in fours:
                        fours.append(i)
                # print("单排", ones)
                # print("对牌", twos)
                # print("四张", fours)
                # 四张牌为1次单张牌或对牌出现2次
                is_sidaier = (len(fours) == 1 and len(ones) == 2) or (len(fours) == 1 and len(twos) == 2)
                if is_sidaier:
                    print("是4带2")
                return is_sidaier
            else:
                return False

        dan = is_dan()
        dui = is_dui()
        shun = is_shun()
        liandui = is_liandui()
        sanzhang = is_sanzhang()
        sandaiyi = is_sandaiyi()
        sandaier = is_sandaier()
        sidaier = is_sidaier()
        zha = is_zha()
        feiji = is_feiji()
        return dan or dui or shun or liandui or sanzhang or sandaiyi or sandaier or sidaier or zha or feiji

    def game_init(self, sockfd, uname):
        """
        界面初始化方法
        """
        # 开启进程负责与服务器数据交互
        t = Thread(target=self.send_recv, args=(sockfd, uname))
        t.daemon = True
        t.start()
        pygame.init()
        self.top = pygame.display.set_mode((1600, 800))
        pygame.display.set_caption(uname)
        background = pygame.image.load('../images/beijing/new.jpg')
        background = pygame.transform.scale(background, (1600, 800))
        start_game = pygame.image.load('../images/play/start.png')
        start_game = pygame.transform.scale(start_game, (160, 50))
        pipei = pygame.image.load('../images/play/pipei.png')
        pipei = pygame.transform.scale(pipei, (160, 50))
        send = pygame.image.load('../images/play/chupai.png')
        send = pygame.transform.scale(send, (120, 50))
        not_send = pygame.image.load('../images/play/buchu.png')
        not_send = pygame.transform.scale(not_send, (120, 50))
        qiang = pygame.image.load('../images/play/qiangdizhu.png')
        qiang = pygame.transform.scale(qiang, (120, 50))
        bqiang = pygame.image.load('../images/play/buqiang.png')
        bqiang = pygame.transform.scale(bqiang, (120, 50))
        fanmian = pygame.image.load('../images/pai/fanmian.png')
        fanmian = pygame.transform.scale(fanmian, (110, 150))
        # 地主头像展示
        dizhu = pygame.image.load('../images/touxiang/dizhu.png')
        dizhu = pygame.transform.scale(dizhu, (130, 150))
        # 农民头像展示
        nong = pygame.image.load('../images/touxiang/nongmin.png')
        # nong = pygame.transform.scale(nong, (110, 150))
        # 牌不合法提示
        guize = pygame.image.load('../images/play/guize.png')
        guize = pygame.transform.scale(guize, (400, 50))

        # 输赢图片展示
        # 地主赢图片展示
        dizhu_win = pygame.image.load('../images/play/dzwin.png')
        dizhu_win = pygame.transform.scale(dizhu_win, (800, 300))

        # 地主输图片展示
        dizhu_fail = pygame.image.load('../images/play/dzfail.png')
        dizhu_fail = pygame.transform.scale(dizhu_fail, (800, 300))

        # 农民赢图片展示
        nong_win = pygame.image.load('../images/play/nmwin.png')
        nong_win = pygame.transform.scale(nong_win, (800, 300))

        # 农民输图片展示
        nong_fail = pygame.image.load('../images/play/nmfail.png')
        nong_fail = pygame.transform.scale(nong_fail, (800, 300))

        # 倍数图片
        bei = pygame.image.load('../images/play/bei.png')
        bei = pygame.transform.scale(bei, (50, 50))
        while True:
            # 倍数数字
            bs = pygame.font.Font('../font/Roboto-Bold.ttf', 60)
            bs = bs.render("{}".format(self.bei), True, (44, 237, 232))
            # 事件监控
            going = self.event_function(sockfd, uname)
            if going:
                print("结束了")
                return
            # 画背景
            self.top.blit(background, (0, 0))
            self.top.blit(bei, (1300, 750))
            self.top.blit(bs, (1400, 740))

            # 刷新自己剩余的牌
            if self.flush_position:
                print("刷新了一次")
                self.set_card_position()
                # 刷新一次之后就不等待下次出完牌之后刷新
                self.flush_position = False

            # 画头像
            if self.is_dizhu:
                # print("111")
                self.top.blit(dizhu, (10, 640))
                self.top.blit(nong, (90, 50))
                self.top.blit(nong, (1300, 50))
            # 画头像
            if self.is_nong:
                self.top.blit(nong, (10, 640))
                self.top.blit(dizhu, (1300, 50))
                self.top.blit(nong, (90, 50))

            # 画抢地主按钮
            if self.is_qiang:
                self.top.blit(qiang, (500, 550))
                self.top.blit(bqiang, (650, 550))

            # 画底牌
            if self.di:
                di_position = []
                x = 500
                for i in self.di:
                    a = ['../images/pai/' + i + ".png", x, 20]
                    x += 110
                    di_position.append(a)
                for i in di_position:
                    di = pygame.image.load(i[0])
                    di = pygame.transform.scale(di, (110, 150))
                    self.top.blit(di, (i[1], i[2]))

            # 画匹配按钮
            if self.pipei:
                self.top.blit(pipei, (650, 500))

            # 画开始按钮
            if self.kaishi:
                self.top.blit(start_game, (650, 550))

            # 画发送按钮
            if self.is_send:
                self.top.blit(send, (650, 530))
                self.top.blit(not_send, (820, 530))

            # 画其他玩家牌的反面
            if self.is_have_card:
                self.draw_fanmian(fanmian)
            # 画发送的牌
            if self.select_cards_show:
                self.draw_send_card(sockfd, uname)
                self.show_history = False

            # 画提示语
            if self.guize:
                self.top.blit(guize, (600, 580))

            # 画上家出的牌
            if self.show_history:
                # 显示上家发送的牌
                self.set_history_card_position()
                self.draw_history_card()

            # 画自己的牌
            self.draw_card()

            # 根据输赢画显示的图片
            if self.dizhu_win:
                self.top.blit(dizhu_win, (400, 300))
            elif self.dizhu_fail:
                self.top.blit(dizhu_fail, (400, 300))
            elif self.nong_win:
                self.top.blit(nong_win, (400, 300))
            elif self.nong_fail:
                self.top.blit(nong_fail, (400, 300))

            pygame.display.update()
            time.sleep(0.1)

    def get_game_addr(self):
        """
        获取服务器的游戏套接字地址
        """
        # 读取配置文件获取端口号和主机地址
        with open('/mnt/hgfs/share/untitled/斗地主/config/play_config.txt', 'r') as f:
            data = f.read()
            new_data = json.loads(data)
            host = new_data['host']
            port = new_data['port']
        return (host, port)

    # 是否为炸
    def is_zha(self, cards):
        def get_value(card):
            """
            获取牌的值
            """
            dian_index = card.find('.')
            value = int(card[2:dian_index])
            return value

        if len(cards) == 4:
            values = []
            for i in cards:
                values.append(get_value(i))
            for i in values:
                if values.count(i) == 4:
                    print("是炸")
                    return True
                else:
                    return False
        else:
            # 是否为王炸
            if len(self.select_cards) == 2:
                values = []
                for i in self.select_cards:
                    values.append(get_value(i[0]))
                if 2000 in values and 1000 in values:
                    print("是王炸")
                    return True
            return False

    def event_function(self, sockfd, uname):
        """
        事件监听函数
        """
        # 获取服务器的游戏地址
        addr = self.get_game_addr()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("exit")
                pygame.quit()
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 鼠标左键被按下
                if pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    # 判断是否在开始游戏按钮范围内
                    if 650 <= x <= 810 and 550 <= y <= 600 and self.kaishi:
                        self.kaishi = False
                        # 发送准备开始的消息
                        data = "{}:{}".format('ready', uname)
                        sockfd.sendto(data.encode(), addr)
                        print("发送了准备消息")
                    # 发送改变端口请求
                    if 650 <= x <= 810 and 500 <= y <= 550 and self.pipei:
                        self.pipei = False
                        data = "{}:{}".format('change_port', uname)
                        sockfd.sendto(data.encode(), addr)
                        print("发送改变port请求")
                    # 判断是否点击出牌按钮
                    if 650 <= x <= 770 and 530 <= y <= 580 and self.is_send:
                        print("发送牌了")

                        # 设置选中牌的顺序
                        self.select_cards = sorted(self.select_cards, key=self.sorted_hidden_card)

                        print("排序后的选中牌")
                        print(self.select_cards)
                        send_cards = []
                        for i in self.select_cards:
                            send_cards.append(i[0])
                        # 如果上次出牌的还是自己的话,那么自己自由出牌
                        if self.history_name == uname:
                            self.card_num = 0
                            print("上次出牌还是自己")
                        if self.card_num > 0:
                            value = self.get_card_value(send_cards)
                            pt = self.rule() and self.card_num == len(send_cards) and value > self.value
                            zha = self.is_zha(send_cards) and value > self.value
                            # 如果自己出的牌是炸则倍数翻倍
                            if self.is_zha(send_cards):
                                self.bei *= 2
                                print("自己牌是炸翻倍")
                            # 判断牌的规则和值比较
                            if pt or zha:
                                cards = ""
                                # 取出牌
                                for i in self.select_cards:
                                    cards += (":" + i[0])
                                # 如果出的是最后的牌则附加结束消息
                                if len(self.cards) == len(self.select_cards):
                                    num = 0
                                    self.is_win = True
                                    # 结算
                                    self.set_money(uname)
                                    if self.is_dizhu:
                                        self.dizhu_win = True
                                    else:
                                        self.nong_win = True
                                else:
                                    num = len(self.cards) - len(self.select_cards)
                                data = "send_card:{}{}:{}".format(uname, cards, num)
                                sockfd.sendto(data.encode(), addr)
                                self.flush_position = True
                                self.select_cards_show = True
                                self.set_send_card_position(sockfd, uname)
                                self.is_send = False
                                # 把上次出牌人的姓名设置为自己
                                self.history_name = uname
                            else:
                                self.guize = True
                                print("您出的牌不合法")
                        else:
                            # 如果是头一次出牌
                            if self.rule():
                                # 如果自己出的牌是炸则倍数翻倍
                                if self.is_zha(send_cards):
                                    self.bei *= 2
                                    print("自己牌是炸翻倍")
                                cards = ""
                                # 取出牌
                                for i in self.select_cards:
                                    cards += (":" + i[0])
                                if len(self.cards) == len(self.select_cards):
                                    num = 0
                                    self.is_win = True
                                    # 结算
                                    self.set_money(uname)
                                    if self.is_dizhu:
                                        self.dizhu_win = True
                                    else:
                                        self.nong_win = True
                                else:
                                    num = len(self.cards) - len(self.select_cards)
                                data = "send_card:{}{}:{}".format(uname, cards, num)
                                sockfd.sendto(data.encode(), addr)
                                # 把上次出牌人的姓名设置为自己
                                self.history_name = uname
                                self.flush_position = True
                                self.select_cards_show = True
                                self.set_send_card_position(sockfd, uname)
                                self.is_send = False
                            else:
                                self.guize = True
                                print("您出的牌不合法")
                    # 判断是否点击了不出
                    # 820, 530
                    # 120, 50
                    if 820 <= x <= 940 and 530 <= y <= 580 and self.is_send:
                        sockfd.sendto("pass:".encode(), addr)
                        self.is_send = False
                    # 判断是否点击了抢地主
                    if 500 <= x <= 620 and 500 <= y <= 600 and self.is_qiang:
                        data = '{}:{}'.format('qiang', 'q')
                        sockfd.sendto(data.encode(), addr)
                        # 改变标志位，显示抢地主
                        self.is_qiang = False
                        # 抢一次地主翻倍
                        self.bei = self.bei * 2
                    # 判断是否点击了不抢
                    if 650 <= x <= 770 and 500 <= y <= 600 and self.is_qiang:
                        data = '{}:{}'.format('qiang', 'bq')
                        sockfd.sendto(data.encode(), addr)
                        self.is_qiang = False
                        # print("发送了不强地主消息")
                    if 200 <= x <= 1350 and 650 <= y <= 800:
                        # 重新选择牌让提示消失
                        self.guize = False
                        # 循环全部牌的位置, 判断是否在这区域
                        for index, i in enumerate(self.card_position, start=1):
                            # 设置最后一张牌全张牌都可以点击,发生监听事件
                            if index == len(self.card_position):
                                # 判断点击的那张牌
                                if i[1] <= x <= i[1] + 110 and i[2] <= y <= 800:
                                    if not i[3]:
                                        print(i[0], ": 被选中")
                                        i[2] -= 50
                                        i[3] = not i[3]
                                        # 如果牌被选中那么就把牌放进列表中
                                        self.select_cards.append(i)

                                    else:
                                        print(i[0], ": 取消选中")
                                        i[2] += 50
                                        i[3] = not i[3]
                                        # 如果牌取消选中则移除牌
                                        self.select_cards.remove(i)
                            else:
                                # 判断点击的那张牌
                                if i[1] <= x <= i[1] + 50 and i[2] <= y <= 800:
                                    if not i[3]:

                                        i[2] -= 50
                                        i[3] = not i[3]
                                        # 如果牌被选中那么就把牌放进列表中
                                        self.select_cards.append(i)
                                        print(i[0], ": 被选中")

                                    else:
                                        i[2] += 50
                                        i[3] = not i[3]
                                        # 如果牌取消选中则移除牌
                                        self.select_cards.remove(i)
                                        print(i[0], ": 取消选中")

    def card_sort(self, name):
        """
        牌排序
        """
        'ht10.png'
        index = name.find('.')
        value = int(name[2:index])
        return value

    def set_card_position(self):
        """
        设置牌的显示位置
        """
        # 在每次初始化位置时要把上次剩余数据清空
        self.card_position = []
        x = 200
        for i in self.cards:
            for j in self.select_cards:
                if j[0] == i:
                    position = [i, x, 650, True]
                    break
            else:
                position = [i, x, 650, False]
            self.card_position.append(position)
            x += 50

    def draw_card(self):
        """
        显示牌
        """
        for i in self.card_position:
            image = pygame.image.load('../images/pai/{}'.format(i[0]))
            image = pygame.transform.scale(image, (110, 150))
            self.top.blit(image, (i[1], i[2]))

    def sorted_hidden_card(self, card):
        """
        发送牌排序
        """
        new_card = card[0]
        index = new_card.find('.')
        value = int(new_card[2:index])
        return value

    def set_send_card_position(self, sockfd, uname):
        """
        设置发送牌的显示位置
        """
        for index, i in enumerate(self.select_cards, start=0):
            i[1] = self.send_card_showx + index * 50
            i[2] = self.send_card_showy
            # 从牌的列表中删除相应的牌
            for j in self.cards:
                if i[0] == j:
                    self.cards.remove(j)
        # 把确定出的牌放在消失列表里
        self.hidden_card = copy.deepcopy(self.select_cards)
        # 牌发出之后就没有选中的牌所以要清空选中列表
        self.select_cards = []

    def draw_send_card(self, sockfd, uname):
        """
        画发送的牌
        """
        for i in self.hidden_card:
            image = pygame.image.load(self.card_path + i[0])
            self.top.blit(image, (i[1], i[2]))
            # 同时删除在总牌列表中的牌
            if i[0] in self.cards:
                # print("删除中")
                self.cards.remove(i[0])

    def set_history_card_position(self):
        """
        设置上家发送牌的显示位置
        """
        history_card = []
        for index, i in enumerate(self.history_card, start=0):
            # 把牌格式化数据结构
            card = []
            card.append(i)
            card.append(self.send_card_showx + index * 50)
            card.append(self.send_card_showy)
            history_card.append(card)
        self.show_history_card = history_card

    def draw_history_card(self):
        """
        画上家发送的牌
        """
        for i in self.show_history_card:
            image = pygame.image.load(self.card_path + i[0])
            self.top.blit(image, (i[1], i[2]))


def main(uname=' '):
    """
    主逻辑函数
    """

    play = Play()
    play.set_card_position()
    # play.cards = ['ht3.png', 'ht4.png', 'ht5.png', 'ht6.png', 'ht7.png', 'ht3.png', 'ht4.png', 'ht5.png', 'ht6.png',
    #               'ht7.png', ]
    # play.flush_position = True
    # play.is_send = True
    sockfd = socket(AF_INET, SOCK_DGRAM)
    play.game_init(sockfd, uname)


if __name__ == '__main__':
    main()
