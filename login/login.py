#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  login.py
#    @Author        :  搏鲨
#    @Create date   :  18-9-4 下午10:22
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""   """
from tkinter import *
import random
from PIL import ImageTk
from tkinter.messagebox import *
import os, sys
import json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
print(BASE_DIR)
print(sys.path)
from register import register
from main import home
from models import MySQL
from socket import *


class Login(object):
    """
    登录类
    """

    def __init__(self):
        """
        保存用户数据
        """
        self.uname = ''

    def get_client_addr(self):
        # 读取配置文件获取端口号和主机地址
        with open('/mnt/hgfs/share/untitled/斗地主/network/client_config.txt', 'r') as f:
            data = f.read()
            new_data = json.loads(data)
            host = new_data['host']
            port = new_data['port']
        return host, port

    def get_host_addr(self):
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

    def to_register(self, top):
        """
        从登录页面跳转到注册页面
        """
        top.destroy()
        register.main()

    def geshi(self, user, pwd, yzm, yzm_word, db):
        """
        用户数据验证
        """
        # 特殊字符验证
        tszf = True
        print("user: ", user)
        print("pwd: ", pwd)
        for i in [user, pwd]:
            if ('\'' in i) or ('"' in i) or ('\\' in i):
                print("------")
                tszf = False
        # 验证码验证
        yanzhengma = (yzm.lower() == yzm_word.lower())
        # 长度验证
        length = True
        for i in [user, pwd]:
            if 6 > len(i) or len(i) > 10:
                length = False

        # 非空验证
        if user and pwd and yzm:
            if not tszf:
                showerror(title="错误信息", message='用户名,密码中不能包含特殊字符')
            if not length:
                showerror(title="错误信息", message='请输入6-10位的用户名或密码')
            if not yanzhengma:
                showerror(title="错误信息", message='验证码错误')
            if tszf and yanzhengma and length:
                # 用户密码正确性
                db.getdatabase()
                sql = "select * from user where username='{}' and password='{}';".format(user, pwd)
                is_have = db.start(sql)
                if is_have:
                    # 查询完数据关闭连接
                    db.close()
                    return True
                else:
                    showerror(title="错误信息", message='用户名或密码错误')
                    return False
        else:
            showerror(title="错误信息", message='用户名,密码,确认密码,验证码不能为空')
            return False

    def yanzheng(self):
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

    def checked(self, top, user, pwd, yzm, yzm_word):
        """注册验证函数"""
        db = MySQL.MySQL('localhost', 3306, 'root', '123456', 'doudizhu', 'utf8')
        # 获取输入框的内容
        user = user.get()
        pwd = pwd.get()
        yzms = yzm.get()
        print(">>>", yzms)
        # 调用格式验证函数
        is_true = self.geshi(user, pwd, yzms, yzm_word, db)
        if is_true:
            self.uname = user
            print(self.uname)
            showinfo(title='登录', message='登陆成功')
            print("登陆成功")
            # 获取本机ip地址
            ip, port = self.get_client_addr()
            # 给服务器发送登录请求
            data = "{}:{}".format('login', self.uname).encode()
            # 获取服务器地址
            addr = self.get_host_addr()
            sockfd = socket(AF_INET, SOCK_DGRAM)
            sockfd.sendto(data, addr)
            # 登陆成功后关闭窗口
            top.destroy()
            # 登录成功之后跳转到用户主界面
            home.init(self.uname, sockfd)


        else:
            showerror(title='登录', message='登录失败')
            print("登录失败")
            return False

    def init(self):
        """初始化界面"""
        top = Tk()
        print("进程创建cd")
        top.config(bg='#DEB887')
        top.title("搏鲨斗地主登录")
        img = ImageTk.PhotoImage(file='../images/tubiao/t1.png')
        tubiao = Label(top, image=img, width=100)
        tubiao.bm = img
        # 设置图标
        ico = PhotoImage(file='../images/tubiao/shark.png')
        top.tk.call('wm', 'iconphoto', top._w, ico)
        top.geometry("530x500")
        titlt = Label(top, text='Shark', font='STKAITI.TTF -40 bold', bg='#DEB887')
        username = Label(top, text="用  户  名：", bg='#DEB887', font='STKAITI.TTF -30 bold')
        password = Label(top, text="密        码:", bg='#DEB887', font='STKAITI.TTF -30 bold')
        yanzhengma = Label(top, text="验  证  码:", bg='#DEB887', font='STKAITI.TTF -30 bold')
        dxx = Label(top, text="不区分大小写", bg='#DEB887', font='STKAITI.TTF -15 bold', fg="#800000")

        # 获取验证码
        s = self.yanzheng()
        s1 = "{} {} {} {}".format(s[0], s[1], s[2], s[3])
        # 验证码数据
        yzm_str = "{}{}{}{}".format(s[0], s[1], s[2], s[3])

        yazhengma_word = Label(top, text=s1, fg='#FF00FF', font='STKAITI.TTF -30 bold', bg='#BDB76B')
        # 用户名输入框
        userinput = Entry(top, width=25, font='STKAITI.TTF -20 bold')
        # 密码输入框
        passinput = Entry(top, width=25, show="*", font='STKAITI.TTF -20 bold')
        # 验证码输入框
        yanzhenginput = Entry(top, width=10, font='STKAITI.TTF -20 bold')
        # 登录按钮
        login_button = Button(top, text="登录", width=8, height=1, bg='#B8860B', activebackground='#FFD700', fg="#0000cd",
                              font='STKAITI.TTF -18 bold',
                              command=lambda top=top, user=userinput, pwd=passinput, yzm=yanzhenginput,
                                             yzm_word=yzm_str: self.checked(top, user, pwd, yzm,
                                                                            yzm_word))
        register_button = Button(top, text="注册", width=8, height=1, bg='#B8860B', activebackground='#FFD700',
                                 fg="#800000",
                                 font='STKAITI.TTF -18 bold', command=lambda top=top: self.to_register(top))
        titlt.place(x=270, y=10)
        tubiao.place(x=150, y=0)
        username.place(x=10, y=170)
        userinput.place(x=160, y=180)
        password.place(x=10, y=250)
        passinput.place(x=160, y=260)
        yanzhengma.place(x=10, y=330)
        yanzhenginput.place(x=160, y=340)
        yazhengma_word.place(x=300, y=340)
        dxx.place(x=410, y=350)
        register_button.place(x=30, y=440)
        login_button.place(x=300, y=440)
        mainloop()


def main():
    login = Login()
    login.init()


if __name__ == '__main__':
    main()
