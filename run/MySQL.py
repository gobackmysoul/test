#!/usr/bin/python3.5
#    -*- coding:utf-8 -*-  
#    @Filename      :  MySQL_link.py
#    @Author        :  搏鲨
#    @Create date   :  18-5-9 下午8:12
#    @Email         :  1170120381@qq.com
#    @QQ            :  1170120381
#    @Blog          :  http://www.cnblogs.com/bosha/
#    @license       :  (C) Copyright 2018-2020,  搏鲨所有.
"""  利用类封装连接数据库代码 """
import pymysql


class MySQL:
    def __init__(self, server, port, user, pawd, database, charset):
        self.server = server
        self.port = port
        self.user = user
        self.pawd = pawd
        self.database = database
        self.charset = charset

    def getdatabase(self):
        """获取数据库连接,以及游标"""
        self.conn = pymysql.connect(host=self.server, port=self.port, user=self.user, passwd=self.pawd,
                                    db=self.database,
                                    charset=self.charset)
        self.cursor = self.conn.cursor()

    def close(self):
        """关闭游标以及数据库连接"""
        self.conn.close()
        self.cursor.close()

    def start(self, sql):
        """执行sql语句获取结果"""
        try:
            self.cursor.execute(sql)  # 执行sql语句
            self.conn.commit()  # 提交事务
            return self.cursor.fetchall()  # 返回执行结果
        except:
            print("操作失败！")
            return "error"

