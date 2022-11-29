import os
import json
import requests
from lxml import etree
from tqdm import tqdm
import pandas as pd
import datetime
import re


#下载时间,阅读,评论,标题,作者,作者ID,贴子链接,发帖时间
def get_items(url,pr,timeout=10):
    #resp = requests.get(url,timeout=timeout).content
    resp = pr.get_request(url).content
    parser = etree.HTML(resp)
    divs = parser.xpath('//*[@id="articlelistnew"]/div')[1:-2]
    items = []
    now = datetime.datetime.today().strftime("%Y/%m/%d")
    for div in divs:
        #阅读
        yuedu = div.xpath('span[@class="l1 a1"]/text()')
        #评论
        pinglun = div.xpath('span[@class="l2 a2"]/text()')
        #标题
        biaoti = div.xpath('span[@class="l3 a3"]/a/text()')
        #作者
        zuoze = div.xpath('span[@class="l4 a4"]/a//text()')
        #作者ID
        zuozeID = div.xpath('span[@class="l4 a4"]/a/@data-popper')
        #帖子链接
        tieziurl = div.xpath('span[@class="l3 a3"]/a/@href')
        #发帖时间
        tieziTime = div.xpath('span[@class="l5 a5"]/text()')
        item = [now,yuedu,pinglun,biaoti,zuoze,zuozeID,tieziurl,tieziTime]
        items.append(item)
    return items


def get_date(url,pr):
    if "caifuhao.eastmoney.com/news/2" in url:
        return [url[url.index("news/")+5:url.index("news/")+19]]
        
    resp = pr.get_request(url).content
    date = re.findall('"post_publish_time":"(.*?)"',resp.decode('utf-8'))
    return date


def fill_year(items,pr):
    i=0
    k=len(items)-1
    dates = {}
    while i<=k:
       
        if i not in dates:
            url =  "http:"+items[i][6][0] if items[i][6][0][:2]=="//" else "http://guba.eastmoney.com"+items[i][6][0]
            dates[i] = get_date(url,pr)
            n = i+1
            while not dates[i]:
                url =  "http:"+items[n][6][0] if items[n][6][0][:2]=="//" else "http://guba.eastmoney.com"+items[n][6][0]
                dates[i] = get_date(url,pr)
                n+=1
                
        if k not in dates:
            url =  "http:"+items[k][6][0] if items[k][6][0][:2]=="//" else "http://guba.eastmoney.com"+items[k][6][0]
            dates[k] = get_date(url,pr)
            n = k-1
            while not dates[i]:
                url =  "http:"+items[n][6][0] if items[n][6][0][:2]=="//" else "http://guba.eastmoney.com"+items[n][6][0]
                dates[k] = get_date(url,pr)
                n -= 1
        try:
            if dates[i][0][:4] == dates[k][0][:4]:
                for ii in range(i,k+1):
                    items[ii][7] = dates[k][0][:4]+"-"+items[ii][7][0]
                i=k+1
                k = len(items)-1
            else:
                k = (i+k)//2
        except:
            print("dates[i]={},i={}",dates[i],i)
            print("dates[k]={},i={}",dates[k],k)
            print("-------")
            if dates[i]:
                year = dates[i][0][:4]
            elif dates[k]:
                year = dates[k][0][:4]
            else:
                year = ""
            
            for ii in range(i,k+1):
                try:
                    items[ii][7] = year+"-"+items[ii][7][0]
                    i=k+1
                    k = len(items)-1
                except:
                    items[ii][7] = ""
                    i=k+1
                    k = len(items)-1
            
    return items
                
        

def add_to_df(items,df,dates,now_date_i):
    i = now_date_i
    df_i = len(df)
    for ii in range(len(items)):
        if not items[ii][7]:continue
        date = items[ii][7][0]
        while not date[:5] == dates[i].strftime("%Y-%m-%d")[-5:]:
            i+=1
        items[ii][7] = dates[i].strftime("%Y-%m-%d")[:5]+date
        #添加到dataframe
        if not items[ii][1]:items[ii][1]=["0"]
        if not items[ii][2]:items[ii][2]=["0"]
        if not items[ii][3]:items[ii][3]=[""]
        if not items[ii][4]:items[ii][4]=[""]
        if not items[ii][5]:items[ii][5]=[""]
        if not items[ii][6]:items[ii][6]=[""]
        #帖子链接有两种格式
        items[ii][6] =  "http:"+items[ii][6][0] if items[ii][6][0][:2]=="//" else "http://guba.eastmoney.com"+items[ii][6][0]
        if "万" in items[ii][1][0]:items[ii][1][0] = int(float(items[ii][1][0][:-1])*10000)
        df.loc[df_i+ii] = [items[ii][0],\
                      int(items[ii][1][0]),\
                      int(items[ii][2][0]),\
                          items[ii][3][0],\
                          items[ii][4][0],\
                          items[ii][5][0],\
                          items[ii][6],\
                          items[ii][7]]
    return df,i


def add_to_df2(items,df):
    df_i = len(df)
    for ii in range(len(items)):
        #检测是否为空
        if not items[ii][1]:items[ii][1]=["0"]
        if not items[ii][2]:items[ii][2]=["0"]
        if not items[ii][3]:items[ii][3]=[""]
        if not items[ii][4]:items[ii][4]=[""]
        if not items[ii][5]:items[ii][5]=[""]
        if not items[ii][6]:items[ii][6]=[""]
        if "万" in items[ii][1][0]:items[ii][1][0] = int(float(items[ii][1][0][:-1])*10000)
        #帖子链接有两种格式
        items[ii][6] =  "http:"+items[ii][6][0] if items[ii][6][0][:2]=="//" else "http://guba.eastmoney.com"+items[ii][6][0]
        
        
        df.loc[df_i+ii] = [items[ii][0],\
                      int(items[ii][1][0]),\
                      int(items[ii][2][0]),\
                          items[ii][3][0],\
                          items[ii][4][0],\
                          items[ii][5][0],\
                          items[ii][6],\
                          items[ii][7]]
    return df






# #transform to csv

# savedir = "out/000001"
# files = [(int(i.split(".")[0]),i) for i in os.listdir(savedir)]
# files.sort()

# items = []
# for i in tqdm(files):
#     with open(os.path.join(savedir,i[1])) as f:
#         items = items+json.loads(f.read())
        
# df = pd.DataFrame(columns=["下载时间yyyymmdd","阅读","评论","标题","作者","作者ID","贴子链接","发帖时间yyyymmdd"])

# start_date = "2000-01-01"
# end_date = "2022-7-3"
# dates = pd.date_range(start_date,end_date,freq="1D")[::-1]

# i=0
# df,i = add_to_df(items[:80],df,dates,now_date_i=i)












# savedir = "out/000001"
# files = [(int(i.split(".")[0]),i) for i in os.listdir(savedir)]
# files.sort()

# start_date = "2000-01-01"
# end_date = "2022-7-3"
# dates = pd.date_range(start_date,end_date,freq="1D")[::-1]

# items = []
# for i in tqdm(files):
#     with open(os.path.join(savedir,i[1])) as f:
#         items = items+json.loads(f.read())
        
# df = pd.DataFrame(columns=["下载时间yyyymmdd","阅读","评论","标题","作者","作者ID","贴子链接","发帖时间yyyymmdd"])
# i = 0
# for ii in tqdm(range(len(items))):
#     date = items[ii][7][0]
#     while not date[:5] == dates[i].strftime("%Y-%m-%d")[-5:]:
#         i+=1
#     items[ii][7] = dates[i].strftime("%Y-%m-%d")[:5]+date
#     #添加到dataframe
#     #作者ID 可能为空
#     if not items[ii][5]:items[ii][5]=[""]
#     #帖子链接有两种格式
#     items[ii][6] =  "http:"+items[ii][6][0] if items[ii][6][0][:2]=="//" else "http://guba.eastmoney.com"+items[ii][6][0]
    
#     df.loc[ii] = [items[ii][0],\
#                   int(items[ii][1][0]),\
#                   int(items[ii][2][0]),\
#                       items[ii][3][0],\
#                       items[ii][4][0],\
#                       items[ii][5][0],\
#                       items[ii][6],\
#                       items[ii][7]]
      
# #df.to_csv("000001.csv")
    
    
    
    
        

    





