#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  chat.py
#    @Author        :  搏鲨
#    @Create date   :  18-9-4 下午11:01
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""
聊天框
"""
from tkinter import *
from tkinter.messagebox import *


def send_message(message, place):
    """
    发送消息
    """
    data = message.get()
    place.config(state=NORMAL)
    if data:
        place.insert(END, data + '\n')
        print(data)
        place.config(state=DISABLED)
    else:
        showerror(title='错误', message='消息不能为空')


def init():
    """
    初始化界面
    """
    # 初始化窗口
    top = Tk()
    top.geometry('513x500')
    top.geometry('+1000+200')
    top.config(bg='#ADD8E6')
    # 标题设置
    top.title("聊天")
    # 游戏图标
    ico = PhotoImage(file='../images/tubiao/shark.png')
    top.tk.call('wm', 'iconphoto', top._w, ico)
    # 消息显示子窗体
    frame = Frame(top)
    # 消息输入框
    input = Entry(top, width=25, font='STKAITI.TTF -27 bold', bd=2)
    # 消息展示面板
    show_message = Text(frame, height=14, width=41, font='STKAITI.TTF -20 bold', state=DISABLED)
    # 发送按钮
    send_button = Button(top, text='发送', width=7, height=2,
                         command=lambda message=input, place=show_message: send_message(message, place), bg='#00ced1',
                         activebackground='#48d1cc', activeforeground='#8a2be2', foreground='#ff1493',font='STKAITI.TTF -15 bold')
    # 消息滚动条
    scrollbar = Scrollbar(frame)
    scrollbar.pack(side=RIGHT, fill=Y)
    show_message.pack(side=LEFT, fill=Y)
    scrollbar.config(command=show_message.yview)
    show_message.config(yscrollcommand=scrollbar.set)
    input.place(x=0, y=452)
    send_button.place(x=415, y=450)
    frame.place(x=0, y=0)
    mainloop()


def main():
    init()


if __name__ == '__main__':
    main()
