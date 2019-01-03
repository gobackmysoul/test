#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  login_test.py
#    @Author        :  搏鲨
#    @Create date   :  18-9-21 下午10:37
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""
 
"""


# def fun():
#     root.destroy()
#     import login
#     login.main()
#
#
# root = Tk()
# root.protocol("WM_DELETE_WINDOW", fun)
# root.mainloop()
# import tkinter
# import tkinter.scrolledtext as scrolledtext
#
# class GUI(object):
#
#     def __init__(self):
#         root = self.root = tkinter.Tk()
#         root.title('Test')
#
#     # make the top right close button minimize (iconify) the main window
#         root.protocol("WM_DELETE_WINDOW", root.iconify)
#
#     # make Esc exit the program
#         root.bind('<Escape>', lambda e: root.destroy())
#
#     # create a menu bar with an Exit command
#         menubar = tkinter.Menu(root)
#         filemenu = tkinter.Menu(menubar, tearoff=0)
#         filemenu.add_command(label="Exit", command=root.destroy)
#         menubar.add_cascade(label="File", menu=filemenu)
#         root.config(menu=menubar)
#
#     # create a Text widget with a Scrollbar attached
#         txt = scrolledtext.ScrolledText(root, undo=True)
#         txt['font'] = ('consolas', '12')
#         txt.pack(expand=True, fill='both')
#
# gui = GUI()
# gui.root.mainloop()
sql = "update user set money=money+{} where username='{}';".format('lyxyly', 10000)
print(sql)