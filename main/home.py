#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  home.py
#    @Author        :  搏鲨
#    @Create date   :  18-9-10 下午9:57
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""
 房间展示
"""
from socket import *
from tkinter import *
from tkinter.messagebox import *
from PIL import ImageTk
import os, sys
import json
from multiprocessing import Process
from threading import Thread
from signal import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from models import MySQL
from main import play

# 房间列表
ROOM_LIST = []


def get_host_addr():
    """
    获取服务器地址
    """
    # 读取配置文件获取端口号和主机地址
    with open('/mnt/hgfs/share/untitled/斗地主/config/server_config.txt', 'r') as f:
        data = f.read()
        new_data = json.loads(data)
        host = new_data['host']
        port = new_data['port']
    return (host, port)


def get_money(uname):
    """
    获取用户余额
    """
    sql = "select money from user where username='{}'".format(uname)
    data = do_sql(sql)
    # 通过下表获取用户余额
    return data[0][0]


def create_homes(sockfd, uname, home_name, home_list):
    """
    创建房间列表
    """
    name = home_name.get('1.0', '1.20')
    # 判断房间名是否为空
    if name:
        try:
            if name not in ROOM_LIST:
                # 获取本机地址
                # 发送创建房间请求
                data = "{}:{}:{}".format('create', name, uname)
                sockfd.sendto(data.encode(), get_host_addr())
                print("房间创建请求发送")
            else:
                showerror(message='房间已存在')
        except Exception as e:
            showerror(message='创建房间失败')
            print("create_room_error: ", e)
    else:
        # 弹窗提示
        showerror(message='房间名不能为空!')


def addmoney(money, dw):
    """
    鲨鱼鳍充值
    """
    old_money = str(money['text'])
    print('old_money', old_money)
    if '.' in old_money:
        dian = old_money.find('.')
        # 取出万的基数
        wan = old_money[0:dian]
        # 取出千的基数
        qian = old_money[dian + 1:]
        # 把千转换成整数
        qmonry = int(qian) * (10 ** (4 - len(qian)))
        # 把万转换成钱数
        wmoney = int(wan) * 10000
        # 把钱转换成整数
        zmoney = qmonry + wmoney
        # 增加原有钱数
        new_money = zmoney + 5000
        print(new_money)
        new_wan = new_money // 10000
        new_qian = new_money % 10000
        # 12000
        # 把千转换成小数
        if new_qian % 10 == 0:
            q = str(new_qian)[0:3]
        if new_qian % 100 == 0:
            q = str(new_qian)[0:2]
        if new_qian % 1000 == 0:
            q = str(new_qian)[0]
        else:
            q = str(new_qian)[0:]
        print(q)
        money['text'] = '{}.{}'.format(str(new_wan), q)
    else:
        new_money = int(old_money) + 5000
        if new_money > 10000:
            new_wan = new_money // 10000
            new_qian = new_money % 10000
            # 12000
            # 把千转换成小数
            if new_qian % 10 == 0:
                q = str(new_qian)[0:3]
            if new_qian % 100 == 0:
                q = str(new_qian)[0:2]
            if new_qian % 1000 == 0:
                q = str(new_qian)[0]
            money['text'] = '{}.{}'.format(str(new_wan), q)
            # 显示单位
            dw.place(x=460, y=13)

        else:
            money['text'] = '{}'.format(new_money)


def into(sockfd, uname, home):
    """
    进入房间
    """
    room_name = home.get(ACTIVE)
    data = "{}:{}:{}".format('into', room_name, uname)
    # 往服务器发送进入房间请求
    sockfd.sendto(data.encode(), get_host_addr())


def do_sql(sql):
    """
    操作数据库接口
    """
    db = MySQL.MySQL('localhost', 3306, 'root', '123456', 'doudizhu', 'utf8')
    db.getdatabase()
    data = db.start(sql)
    return data


def do_play(uname, umoney):
    """
    开启游戏进程
    """
    # 调用游戏开启函数
    play.main(uname)
    print("窗口销毁")
    print("回到home下")
    # 游戏结束回到用户主界面
    # 刷新余额
    money = get_money(uname)
    umoney.set(money)
    top.update()
    top.deiconify()


def insert_room(room_list, sockfd, top, uname, umoney):
    """
    增加房间列表函数
    """
    print("线程创建成功")
    while True:
        # try:
        data, addr = sockfd.recvfrom(1024)
        data = data.decode().split(":")
        if data[0] == 'create':
            if data[1] == 'success':
                room_name = data[2]
                room_list.insert(END, room_name)
                # 往房间列表中添加新创建的列表
                ROOM_LIST.append(room_name)
                print("插入成功")
            elif data[1] == 'fail':
                showerror(message="创建房间失败")
            elif data[1] == 'play':
                top.withdraw()
                do_play(uname, umoney)
        elif data[0] == 'room':
            if data[1] == 'success':
                print("进入房间成功")
                top.withdraw()
                play.main(uname)
                top.update()
                top.deiconify()

            elif data[1] == 'full':
                showerror(title="进入房间", message='房间已满')
    # except Exception as e:
    #     print("insert_room_error: ", e)


# def back(sig, frame):
#     """
#     返回用户主界面
#     """
#     if sig == SIGCHLD:
#         print("子进程退出返回用户主界面")
#         # 把用户主界面重新显示到界面
#         main()
# def shuaxin(money, uname):
#     money_lb = money
#     money_lb['text'] = get_money(uname)
#     money_lb.after(5000, shuaxin, money_lb, uname)


def init(uname, sockfd):
    """
    初始化函数
    """
    # 动态获取用户余额

    global top
    top = Tk()
    umoney = IntVar()
    umoney.set(get_money(uname))
    top.title('搏鲨斗地主')
    top.geometry('800x800')
    top.config(bg='#DEB887')
    # 设置图标
    ico = PhotoImage(file='../images/tubiao/shark.png')
    print('-----')
    top.tk.call('wm', 'iconphoto', top._w, ico)
    print("啦啦啦")
    # 用户名
    username = Label(top, text=uname, font='STKAITI.TTF -40 bold', fg='#4682b4', bg='#DEB887')
    # 创建房间
    create_home = Label(top, text='请输入房间名', font='STKAITI.TTF -40 bold', fg='#4682b4', bg='#DEB887')
    print("余额前")
    # 余额图标
    img = ImageTk.PhotoImage(file='../images/tubiao/money1.png')
    money_img = Label(top, image=img, width=50, bg='#DEB887')
    money_img.bm = img
    print("余额后")
    # 余额
    money = Label(top, textvariable=umoney, font='STKAITI.TTF -40 bold', bg='#DEB887', fg='#4682b4')
    # 充值
    img1 = ImageTk.PhotoImage(file='../images/tubiao/add.png')
    add_money1 = Label(top, image=img1, width=50, bg='#DEB887')
    add_money1.bm = img
    # 钱单位(万)
    dw = Label(top, text='万', font='STKAITI.TTF -40 bold', bg='#DEB887', fg='#4682b4')
    # 鲨鱼鳍增加监听
    add_money1.bind('<Button-1>', lambda event, moneys=money, dw=dw: addmoney(moneys, dw))

    # 房间标题
    home = Label(top, text='房间列表', font='STKAITI.TTF -40 bold', bg='#DEB887', fg='#4682b4')
    # 初始化子窗体
    frame = Frame(top, width=500, height=800, bg='#BDB76B')
    # 房间滚动条
    sc = Scrollbar(frame, orient=VERTICAL)

    # 选项
    lb = Listbox(frame, yscrollcommand=sc.set, font='STKAITI.TTF -30 bold')
    # 创建进程监听房间创建,增加房间选项
    t = Thread(target=insert_room, args=(lb, sockfd, top, uname, umoney))
    t.daemon = True
    # 开启进程
    t.start()
    # 进入房间按钮
    goto = Button(top, text='进入', font='STKAITI.TTF -30 bold', width=19, fg='#4682b4', background='#bdb76b',
                  activebackground='#eee8aa', activeforeground='#87ceeb',
                  command=lambda sockfd=sockfd, uname=uname, name=lb: into(sockfd, uname, name))
    # 房间名输入框
    home_name = Text(top, width=20, height=1, font='STKAITI.TTF -30 bold')
    # 创建房间按钮
    create_button = Button(top, text='创建房间', font='STKAITI.TTF -30 bold', width=10, fg='#4682b4', background='#bdb76b',
                           activebackground='#eee8aa', activeforeground='#87ceeb',
                           command=lambda sockfd=sockfd, uanme=uname, home_name=home_name, home_list=lb: create_homes(
                               sockfd, uname, home_name,
                               home_list))

    sc.config(command=lb.yview)
    sc.pack(side=RIGHT, fill=Y)
    lb.pack(side=LEFT, fill=Y)
    home.place(x=10, y=180)
    frame.place(x=0, y=250)
    username.place(x=10, y=10)
    create_home.place(x=500, y=180)
    money.place(x=300, y=10)
    money_img.place(x=230, y=20)
    add_money1.place(x=500, y=28)
    dw.place(x=410, y=13)
    goto.place(x=0, y=730)
    # 隐藏钱单位
    dw.place_forget()
    home_name.place(x=400, y=250)
    create_button.place(x=480, y=350)
    print("各种画")
    mainloop()


def main():
    init(uname='lyxyly', sockfd='')


if __name__ == '__main__':
    main()
