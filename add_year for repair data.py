import pandas as pd
import requests
import re
from tqdm import tqdm
from proxy import Proxy_request      
import datetime
import os
import time
from spider import TillThread
import inspect
import ctypes

#获取单个评论真实评论
def get_date(url,pr=None):
    if "caifuhao.eastmoney.com/news/2" in url:
        date = url[url.index("news/")+5:url.index("news/")+19]
        date = date[:4]+"-"+date[4:6]+"-"+date[6:8]+" "+date[8:10]+":"+date[10:12]+":"+date[12:14]
        return date
    if pr:
        resp = pr.get_request(url).content
    else:
        resp = requests.get(url).content
    date = re.findall('"post_publish_time":"(.*?)"',resp.decode('utf-8'))
    if date:
        date = date[0]
    else:
        date = ""
    return date

#写入数据
def write_to_file(items,csv):
    with open(csv,'w+',encoding='utf8') as f:
        f.write("下载时间yyyymmdd,阅读,评论,标题,作者,作者ID,贴子链接,发帖时间yyyymmdd\n")
        for ii in range(len(items)):
            line = items[ii][1]+\
                        ','+\
                      str(items[ii][3])+\
                          ','+\
                      str(items[ii][4])+\
                          ','+\
                          '"'+items[ii][5]+'"'+\
                          ','+\
                          '"'+items[ii][6]+'"'+\
                          ','+\
                      '"'+str(items[ii][7])+'"'+\
                          ','+\
                          '"'+items[ii][8]+'"'+\
                          ','+\
                          items[ii][9]+\
                          "\n"
            f.write(line)

#读取out文件夹的单个数据    
def read_items(csv):
    with open(csv) as f:
        lines = f.readlines()[1:]
        items = []
        for item in lines:
            try:
                item = item.strip().replace(',,',',"",')
                item = eval("['"+item[:6]+"'"+item[6:]+"]")
                items.append(item)
            except:
                print(item)
        items = sorted(items, key=lambda item: item[2])
        return items

#填充年份
def fill_year(items,dates,pr=None):
    i = 0
    pass2022 = False
    empty_year = False
    old_year = dates[i][:4]
    for ii in range(len(items)):
        old_i = i
        items[ii][-1] = items[ii][-1] if len(items[ii][-1])==11 else items[ii][-1][5:]
        try:
            while dates[i][5:10] != items[ii][-1][:5]:
                i += 1
        except:
            continue
        #检测年份更改
        if dates[i][:4]!=old_year or empty_year or (pass2022 and old_year=='2022' and items[0][0] not in items[ii][-2]) or 'caifuhao' in items[ii][-2]: 
            if dates[i][:4]!=old_year:
                print('different')
                
            if empty_year:
                print('empty')
                
            if (pass2022 and old_year=='2022' and items[0][0] not in items[ii][-2]):
                print("potion")
            
            #获取真实日期
            date = get_date(items[ii][-2],pr)[:4]
            print(date)
            if date==old_year:
                empty_year = False
                items[ii][-1] = old_year+"-"+items[ii][-1]
                i = dates.index(items[ii][-1][:10])
            elif date=="":
                empty_year = True
                print("日期为空")
                print(ii)
                print(items[ii][-2])
                items[ii][-1] = old_year+"-"+items[ii][-1]
            else:
                if date[:4] in ['2021','2020','2019','2018','2017']:
                    pass2022 = True
                else:
                    pass2022 = False
                empty_year = False
                old_year = date
                items[ii][-1] = old_year+"-"+items[ii][-1]
        else:
            items[ii][-1] = old_year+"-"+items[ii][-1]
            
            
    return items

#清除有毒数据
def clear_potion(items):
    ok_items = []
    count = 0
    page = 0
    potion= True
    for i in range(len(items)):
        if page!=items[i][2]:
            #判断上一页是否存在真实，若存在真实，可以直接添加到ok_items
            if not potion:
                for ii in range(i-count,i):
                    ok_items.append(items[ii])
                    #有神秘的出现年份
                    ok_items[-1][-1] = ok_items[-1][-1][-11:]
            else:
                print(i-1)
                print(page)
                if i:
                    with open("potion.txt",'a') as f:
                        line = [page,items[i-1][0],items[i-1][0],items[i-1][-2]]
                        f.write(f'{line}\n')
            
            potion = True
            count = 0
            page = items[i][2]
            
        #判断是否是假数据 
        if items[i][0] in items[i][-2]:
            potion=False
        count += 1
    return ok_items


import os

#加载未填充的codes
codes = os.listdir("repair_data")

#代理接口
pr = Proxy_request()
#填充年份
dates = pd.date_range(start="1980-01-01",end = "2022-12-30",freq="1D").to_list()
dates.reverse()
dates = [i.__str__()[:10] for i in dates]


# #获取今天日期
now = datetime.datetime.today().strftime("%Y%m%d")
error_list = []
for code in tqdm(codes):
    try:
        #读取items
        items = read_items(csv="repair_data/"+code)
        #剔除有毒数据
        #item_ok = clear_potion(items)
        #填充年份
        items = fill_year(items, dates, pr)
            #items = fill_year(item_ok,dates,pr)
        #保存到ok
        now = items[-1][1].replace("/",'')
        write_to_file(items,csv="temporary_data/"+now+"_"+code)
    except:
        error_list.append(code)
        continue
reference = os.listdir("final_data")
for i in range(len(reference)):
    reference[i] = reference[i][9:15]
code_list = []
for i in error_list:
    if i in reference:
        continue
    else:
        code_list.append(i)

#重要补充，出现特殊爬取文件导致上述代码无法运行时，将会自动运行以下补充文件
if code_list:

    def _async_raise(tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")


    def stop_thread(thread):
        _async_raise(thread.ident, SystemExit)

    codes = code_list
    # 保存地址
    savedir = "final_data"
    # 开启线程
    n_threads = 100
    # 线程id
    thread = 0
    # 缓存线程
    threads = []
    # 获取目标地址
    start_date = "2017-01-01"

    # 缓存
    cache_freq = 100
    cache_i = 0
    cache_dir = "cache"
    cache_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    cache_codes = {}
    if os.path.exists(cache_dir):
        cache_codes = dict([(i.split('.')[0], i) for i in os.listdir(cache_dir)])
    else:
        os.makedirs(cache_dir)

    code_i = 0
    code_sum = len(codes)

    # loggin
    from log_test import Logger

    log = Logger('all.log', level='info')
    print = log.logger.info

    while True:
        # 检测线程是否有结束的
        ok = []
        dele = []
        for i in range(len(threads)):
            if ((threads[i].end_date - threads[i].now).days - threads[i].days) >= 0:
                # 保存数据
                threads[i].df.to_csv(os.path.join(threads[i].savedir,
                                                  time.strftime('%Y%m%d', time.localtime(time.time())) + "_" + threads[
                                                      i].code + ".csv"), index=False)
                # 删除相应的缓存文件
                if os.path.exists(os.path.join(cache_dir, threads[i].code + ".csv")):
                    os.remove(os.path.join(cache_dir, threads[i].code + ".csv"))
                dele.append(i)
            else:
                ok.append(i)

        # 关闭线程
        print("ok:" + str(ok))
        print("dele:" + str(dele))
        threads = [threads[i] for i in ok]

        # 添加新的线程
        if code_i < code_sum:
            for i in range(n_threads - len(threads)):
                if code_i < code_sum:
                    code = codes[code_i]
                    t = TillThread(code, savedir, maxtry=5, timeout=10, start_date=start_date, thread_id=code_i)
                    if code in cache_codes:
                        t.df = pd.read_csv(os.path.join(cache_dir, cache_codes[code]))
                        with open(os.path.join('count', code + ".txt")) as f:
                            lines = f.readlines()
                            page = [int(i.split(",")[0]) for i in lines]
                            t.page = max(page) + 1
                    t.start()
                    threads.append(t)
                    code_i += 1

        if not threads:
            break

        # 判断是否需要缓存
        cache_i += 1
        if cache_i % cache_freq == 0:
            print("缓存中。。。。。。")
            for i in range(len(threads)):
                threads[i].df.to_csv(os.path.join(cache_dir, threads[i].code + ".csv"), index=False)
            cache_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print("30s内可以正常退出")

        # 输出进度信息
        os.system("cls")
        print("\n\n总进度(股票条数)： {}/{}".format(code_i, code_sum))
        print("缓存时间：{}\n".format(cache_time))
        for i in range(len(threads)):
            print("code:{} thread {}(天数进度)：{}/{}".format(threads[i].code, threads[i].thread_id,
                                                         (threads[i].end_date - threads[i].now).days, threads[i].days))
        time.sleep(10)

    print("完成运行")
else:
    print("完成运行")
