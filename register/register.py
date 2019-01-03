#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  register.py
#    @Author        :  搏鲨
#    @Create date   :  18-8-26 下午8:28
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""
注册模块
"""
import json
import os
from tkinter import *
import random
from PIL import Image, ImageTk
import pymysql
from models import MySQL
from tkinter.messagebox import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from main import home


def geshi(user, pwd, qpwd, yzm, yzm_word, db):
    """
    用户数据验证
    """
    # 特殊字符验证
    tszf = True
    print("user: ", user)
    print("pwd: ", pwd)
    print('qpwd: ', qpwd)
    for i in [user, pwd, qpwd]:
        if ('\'' in i) or ('"' in i) or ('\\' in i):
            print("------")
            tszf = False
    # 确认密码验证
    qrmm = (pwd == qpwd)
    # 验证码验证
    yanzhengma = (yzm.lower() == yzm_word.lower())
    # 长度验证
    length = True
    for i in [user, pwd]:
        if 6 > len(i) or len(i) > 10:
            length = False

    # 非空验证
    if user and pwd and qpwd and yzm:
        if not tszf:
            showerror(title="错误信息", message='用户名,密码中不能包含特殊字符')
        if not qrmm:
            showerror(title="错误信息", message='确认密码和密码不一致')
        if not length:
            showerror(title="错误信息", message='请输入6-10位的用户名或密码')
        if not yanzhengma:
            showerror(title="错误信息", message='验证码错误')
        if tszf and qrmm and yanzhengma and length:
            # 用户是否存在验证
            db.getdatabase()
            sql = "select * from user where username='{}';".format(user)
            is_have = db.start(sql)
            if not is_have:
                return True
            else:
                showerror(title="错误信息", message='用户已存在')
                return False
                return False
    else:
        showerror(title="错误信息", message='用户名,密码,确认密码,验证码不能为空')
        return False


def model(user, pawd, db):
    """
    操作数据库
    """
    db.getdatabase()
    sql = "insert into user(username, password, money) values('{}','{}', 10000);".format(user, pawd)
    succ = db.start(sql)
    if succ != 'error':
        return True
    else:
        return False


def yanzheng():
    """验证码生成函数"""
    # 验证码存放列表
    yzm = []
    for i in range(65, 91):
        yzm.append(chr(i))
        yzm.append(chr(i + 32))
    for i in range(10):
        yzm.append(i)
    # 将列表顺序打乱
    random.shuffle(yzm)

    # 返回4个验证码字符
    s = random.sample(yzm, 4)
    return s


def get_database_address():
    with open('../config/database', 'r') as f:
        data = json.loads(f.read())
    return data


def register(top, user, pwd, qpwd, yzm, yzm_word):
    """注册验证函数"""
    db = MySQL.MySQL('localhost', 3306, 'root', '123456', 'doudizhu', 'utf8')
    # 获取输入框的内容
    user = user.get()
    pwd = pwd.get()
    qpwd = qpwd.get()
    yzms = yzm.get()
    print(">>>", yzms)
    # 调用格式验证函数
    is_true = geshi(user, pwd, qpwd, yzms, yzm_word, db)
    if is_true:
        # 注册用户操作数据库
        is_succ = model(user, pwd, db)
        if is_succ:
            showinfo(title='注册', message='注册成功')
            print("注册成功")
            top.destroy()
            home.init(user)

        else:
            showinfo(title='注册', message='注册失败')
            print("注册失败")
    else:
        showinfo(title='注册', message='注册失败')
        print("注册失败")


def init():
    """初始化界面"""
    top = Tk()
    top.config(bg='#DEB887')
    top.title("搏鲨斗地主注册")
    img = ImageTk.PhotoImage(file='../images/tubiao/t1.png')
    tubiao = Label(top, image=img, width=100)
    tubiao.bm = img
    ico = PhotoImage(file='../images/tubiao/shark.png')
    top.tk.call('wm', 'iconphoto', top._w, ico)
    top.geometry("530x500")
    titlt = Label(top, text='Shark', font='STKAITI.TTF -40 bold', bg='#DEB887')
    username = Label(top, text="用  户  名：", bg='#DEB887', font='STKAITI.TTF -30 bold')
    password = Label(top, text="密        码:", bg='#DEB887', font='STKAITI.TTF -30 bold')
    qpassword = Label(top, text='确认密码:', bg='#DEB887', font='STKAITI.TTF -30 bold')
    yanzhengma = Label(top, text="验  证  码:", bg='#DEB887', font='STKAITI.TTF -30 bold')
    dxx = Label(top, text="不区分大小写", bg='#DEB887', font='STKAITI.TTF -15 bold', fg="#800000")

    # 获取验证码
    s = yanzheng()
    s1 = "{} {} {} {}".format(s[0], s[1], s[2], s[3])
    # 验证码数据
    yzm_str = "{}{}{}{}".format(s[0], s[1], s[2], s[3])

    yazhengma_word = Label(top, text=s1, fg='#FF00FF', font='STKAITI.TTF -30 bold', bg='#BDB76B')
    # 用户名输入框
    userinput = Entry(top, width=25, font='STKAITI.TTF -20 bold')
    # 密码输入框
    passinput = Entry(top, width=25, show="*", font='STKAITI.TTF -20 bold')
    # 确认密码输入框
    qpassinput = Entry(top, width=25, show='*', font='STKAITI.TTF -20 bold')
    # 验证码输入框
    yanzhenginput = Entry(top, width=10, font='STKAITI.TTF -20 bold')
    # 注册按钮
    register_button = Button(top, text="注册", width=30, height=2, bg='#B8860B', activebackground='#FFD700',
                             command=lambda top=top, user=userinput, pwd=passinput, qpwd=qpassinput, yzm=yanzhenginput,
                                            yzm_word=yzm_str: register(top, user, pwd, qpwd, yzm, yzm_word))
    titlt.place(x=270, y=10)
    tubiao.place(x=150, y=0)
    username.place(x=10, y=100)
    userinput.place(x=160, y=110)
    password.place(x=10, y=180)
    passinput.place(x=160, y=190)
    qpassword.place(x=10, y=250)
    qpassinput.place(x=160, y=260)
    yanzhengma.place(x=10, y=330)
    yanzhenginput.place(x=160, y=340)
    yazhengma_word.place(x=300, y=340)
    dxx.place(x=410, y=350)
    register_button.place(x=130, y=440)


def main():
    init()
    mainloop()


if __name__ == '__main__':
    main()
