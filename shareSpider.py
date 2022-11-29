import os
from utils import get_items,add_to_df
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
        if not end_date:end_date=datetime.datetime.today().strftime("%Y-%m-%d")
        #日历表
        self.dates = pd.date_range('2000-01-01',end_date,freq="1D")[::-1]
        if not os.path.exists(self.savedir):
            os.makedirs(self.savedir)
        #日历表当前顺序
        self.date_now_i = 0
        #url模板
        self.base = "http://guba.eastmoney.com/list,{code},f_{page}.html"
        #页面序号
        self.page = 1
        #start_date
        self.start_date = datetime.datetime.fromisoformat(start_date)
        #扩充日期
        self.datesize = (self.start_date - datetime.datetime.fromisoformat("2000-01-01")).days
        #线程id
        self.thread_id = thread_id
        #proxy
        self.pr = Proxy_request()
    
    
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
            
            now = datetime.datetime.fromisoformat(str(self.dates[self.date_now_i].year)+"-"+self.items[-1][-1][0])
            #添加到df
            self.df,self.date_now_i = add_to_df(self.items,self.df,self.dates,self.date_now_i)
            print("thread:{} code:{}  date:{}/{}   page:{}".format(self.thread_id,self.code,self.date_now_i,len(self.dates)-self.datesize,self.page),end="\n")
            
            #判断日期是否到start_date
            if now<self.start_date:
                break
            
            #加page
            self.page+=1
        #code,page,date_now_i,
        #self.df.to_csv(os.path.join(self.savedir,self.code+"_"+str(self.page)+"_"+str(self.date_now_i)+".csv"))
        self.df.to_csv(os.path.join(self.savedir, time.strftime('%Y%m%d', time.localtime(time.time())) + "_"+ self.code+".csv"))

#pip install xlrd==1.2.0
import xlrd

xlsx = xlrd.open_workbook("etc/codes.xlsx")
sh = xlsx.sheet_by_index(0)
codes = sh.col_values(0)[1:]
codes = codes[3:10]

#保存地址
savedir = "out" 
#开启线程
n_threads = 3
#线程id
thread = 0
#缓存线程
threads = []
#获取目标地址
start_date="2017-01-01"

for code in tqdm(codes):
    t = TillThread(code,savedir,maxtry=5,timeout=10,start_date=start_date,thread_id=thread%10)
    t.start()
    threads.append(t)
    thread+=1
    # if thread%n_threads==0:
    #     while threads:
    #         threads.pop().join()
   








    




















          
# code = "000001"
# savedir = "out" 
# t = TillThread(code,savedir,maxtry=5,timeout=10,start_date="2017-01-01")
# t.start()
# t.join()

# http://guba.eastmoney.com/list,000001,f_1.html
# http://guba.eastmoney.com/list,000001,f_1.html
    
    
# class GetItmeThread(Thread):
#     """
#     code = "000001"
#     maxpage = 5
#     threads = 10
#     save_dir = "out/"        
#     t = GetItmeThread(code=code,maxpage=maxpage,savedir=save_dir,timeout=10)
#     t.start()
#     t.join()
#     """
#     def __init__(self, code,maxpage,savedir,timeout=10):
#         super().__init__()
#         self.errors = []
#         self.code = code
#         self.maxpage = maxpage
#         self.savedir = savedir
#         self.timeout = timeout
        
#         if not os.path.exists(os.path.join(self.savedir,self.code)):
#             os.makedirs(os.path.join(self.savedir,self.code))
    
#     def run(self):
#         base = "http://guba.eastmoney.com/list,{code},f_{page}.html"
#         for page in tqdm(range(1,self.maxpage+1)):
#             url = base.format(code=self.code,page=page)
#             items = None
#             try:
#                 items = get_items(url,timeout=self.timeout)
#             except:
#                 self.errors.append(url)
#             if items:
#                 with open(os.path.join(self.savedir,"%s/%d.json"%(self.code,page)),"w+") as f:
#                     f.write(json.dumps(items))

