# -*- coding: utf-8 -*
 
import time
import random
import requests

class Proxy:
    def __init__(self):
        self.chosen_proxy = ''
        self.PROXY_URL = "http://route.xiongmaodaili.com/xiongmao-web/api/gbip?secret=50515d22deb954a6857711126b4a5d17&orderNo=GB20220711222551zNppxop1&count=5&isTxt=0&proxyType=1"


    def getProxy(self):
        while True:
            try:
                res = requests.get(self.PROXY_URL)
                print(res.text)
            except:
                time.sleep(1)
                continue
            if "请按规定10秒提取一次" in res.text:
                time.sleep(1)
                continue
            else:
                try:
                    proxy_addrs = res.json()['obj']
                except:
                    time.sleep(2)
                    continue
                break
        proxy_addrs = [x['ip'] + ":" + x['port'] for x in proxy_addrs]
        return proxy_addrs


class Proxy_request:

    def __init__(self):
        self.hds = [
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
        ]

        self.proxy = Proxy().getProxy()
        self.proxy_ip = self.get_proxy()
        self.max_conect = 666
        self.connect = 0

    def get_hds(self):
        return {
            'User-Agent': random.choice(self.hds)
        }

    def get_headers(self):
        return {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Length': '11',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'xkz.cbirc.gov.cn',
            'Origin': 'http://xkz.cbirc.gov.cn',
            'Referer': 'http://xkz.cbirc.gov.cn/jr/',
            'User-Agent': random.choice(self.hds),
            'X-Requested-With': 'XMLHttpRequest',
        }

    def get_proxy(self):
        # 单次提取3个IP，用完就从这个method重新提取
        #if len(self.proxy) == 0:
        self.proxy = Proxy().getProxy()
        p = self.proxy.pop()
        ipsss = {"http": "http://" + p, "https": "http://" + p}
        return ipsss

    def post_request(self, link, params=None):
        """
        发起请求
        :param link:
        :return:
        """
        self.connect+=1
        if self.conncet%self.max_connect==0:
            self.proxy_ip = self.get_proxy()
            self.connect=0
        num = 0
        while num < 50:
            try:
                if params is not None:
                    res = requests.post(link, data=params, headers=self.get_headers(), timeout=10, proxies=self.proxy_ip)
                else:
                    res = requests.post(link, headers=self.get_headers(), timeout=100, proxies=self.proxy_ip)
                # 如果页面出现以下结果，则更换IP
                if '请稍后再试' in res.text or "Invalid Request" in res.text or "统正在为您加载数据" in res.text or "Access Denied" in res.text or 'ERR_CACHE_ACCESS_DENIED' in res.text:
                    print(res.text)
                    num = num + 1
                    self.proxy_ip = self.get_proxy()
                    continue
                print(res.text)
                return res
            except:
                print(res.text)
                num = num + 1
                self.proxy_ip = self.get_proxy()
                continue
        if num == 50:
            raise Exception("超过最大重试次数50，抛错，请联系开发检查原因")
        return res

    def get_request(self, link, headers=None):
        """
        发起请求
        :param link:
        :return:
        """
        num = 0
        while num < 50:
            try:
                if headers is None:
                    res = requests.get(link, headers=self.get_hds(), timeout=10, proxies=self.proxy_ip)
                else:
                    res = requests.get(link, headers=self.get_hds(), timeout=10, proxies=self.proxy_ip)
                # 如果页面出现以下结果，则更换IP
                if '请稍后再试' in res.text or "Invalid Request" in res.text or "统正在为您加载数据" in res.text or "Access Denied" in res.text or 'ERR_CACHE_ACCESS_DENIED' in res.text:
                    num = num + 1
                    self.proxy_ip = self.get_proxy()
                    continue
                return res
            except:
                print('error',num)
                num = num + 1
                self.proxy_ip = self.get_proxy()
                continue
        if num == 50:
            raise Exception("超过最大重试次数50，抛错，请联系开发检查原因")
        return res


if __name__ == "__main__":
    pr = Proxy()
    print(pr.getProxy())
