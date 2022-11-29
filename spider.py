import os
from utils import get_items,add_to_df2,fill_year
from threading import Thread
from tqdm import tqdm
import json
import pandas as pd
import datetime
import time   
from proxy_tool import Proxy_request

    
class TillThread(Thread):
    def __init__(self,code,savedir,maxtry=5,timeout=10,start_date="2000-01-01",end_date=None,thread_id=1):
        super().__init__()
        #股票编码
        self.code = code
        #保存地址
        self.savedir = savedir
        #最大尝试次数
        self.maxtry = maxtry
        #requests超时
        self.timeout = timeout
        #h缓存下载的数据
        self.df = pd.DataFrame(columns=["下载时间yyyymmdd","阅读","评论","标题","作者","作者ID","贴子链接","发帖时间yyyymmdd"])
        #判断是否需要至今
        if not end_date:
            self.end_date=datetime.datetime.today()
        else:
            self.end_date = datetime.datetime.fromisoformat(end_date)
        #日历表
        if not os.path.exists(self.savedir):
            os.makedirs(self.savedir)
        
        #url模板
        self.base = "http://guba.eastmoney.com/list,{code},f_{page}.html"
        #页面序号
        self.page = 1
        #start_date
        self.start_date = datetime.datetime.fromisoformat(start_date)
        #线程id
        self.thread_id = thread_id
        #proxy
        self.pr = Proxy_request()
        #总天数 用于显示进度
        self.days = (datetime.datetime.today() - self.start_date).days
        self.now = datetime.datetime.today()
        #线程状态
        self.alive= True
        
    
    def run(self):
        '''
        结束条件
        下载次数超过maxtry
        评论信息到底
        日期到底
        '''
        
        while True:
            url = self.base.format(code=self.code,page=self.page)
            try_num = 0
            #读取
            self.items = []
            while try_num<self.maxtry:
                try:
                    self.items = get_items(url,self.pr,timeout=self.timeout)
                    break
                except:
                    print("error: page:{page} try:{try_num}".format(page=self.page,try_num=try_num))
                try_num+=1
            
            #下载失败 
            if try_num==self.maxtry and not self.items:
                break
            #没有评论信息
            if not self.items:
                break
            
            #填充年份
            try:
                self.items = fill_year(self.items,self.pr)
            except:
                print("fill_year error")
            
            with open("count/{}.txt".format(self.code),'a+') as f:
                f.write("{},{}\n".format(self.page,len(self.items)))
             
            #print("thread:{} code:{}  date:{}/{}   page:{}".format(self.thread_id,self.code,self.date_now_i,len(self.dates)-self.datesize,self.page),end="\n")
            #判断日期是否到start_date
            try:
                self.now = datetime.datetime.fromisoformat(self.items[-1][-1])
            except:
                print(self.items[-1][-1])
                
            if self.now<=self.start_date:
                #添加到df
                #除掉2017年前的数据
                try:
                    for i in range(len(self.items)-1,-1,-1):
                        if int(self.items[i][-1][:4])>=self.start_date.year:
                            break
                    self.df = add_to_df2(self.items[:i+1],self.df)
                    print(self.code,"  ","保存。。。。。",)
                except:
                    print("tail error----")
                break
            #正常添加
            #添加到df
            try:
                self.df = add_to_df2(self.items,self.df)
            except:
                print("base add df error")
            
            #加page
            self.page+=1
            
        #code,page,date_now_i,
        #self.df.to_csv(os.path.join(self.savedir,self.code+"_"+str(self.page)+"_"+str(self.date_now_i)+".csv"))
        self.df.to_csv(os.path.join(self.savedir, time.strftime('%Y%m%d', time.localtime(time.time())) + "_"+ self.code+".csv"),index=False)
        #os.remove(os.path.join('cache',self.code+".csv"))
        




