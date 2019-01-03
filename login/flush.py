#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  flush.py
#    @Author        :  搏鲨
#    @Create date   :  18-9-24 下午12:05
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""
 
"""
from tkinter import *
def rtnkey(event=None):
    e.set(10)
    print(e.get())
root = Tk()
e = StringVar()
entry = Entry(root, validate='key', textvariable=e, width=50)
entry.pack()
entry.bind('<Return>', rtnkey)
root.title('测试回车获取文本框内容')
root.mainloop()



