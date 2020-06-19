import re
from pyquery import PyQuery as pq
import requests
from loguru import logger
from proxypool.utils import Proxy


class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class Crawler(object, metaclass=ProxyMetaclass):   
    def fetch(self, url, **kwargs):
        try:
            response = requests.get(url, **kwargs)
            if response.status_code == 200:
                return response.text
        except requests.ConnectionError:
            return  

    def get_proxies(self, callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            logger.info(f'成功获取到代理 {proxy.string()}')
            proxies.append(proxy)
        return proxies
 
    def crawl_66ip(self, MAX_PAGE=5):
        """
        获取代理66
        """
        BASE_URL1 = 'http://www.66ip.cn/{page}.html'
        urls = [BASE_URL1.format(page=page) for page in range(1, MAX_PAGE)]
        for url in urls:
            logger.info(f'爬取 {url}')
            html = Crawler().fetch(url)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    host = tr.find('td:nth-child(1)').text()
                    port = int(tr.find('td:nth-child(2)').text())
                    yield Proxy(host=host, port=port)
 
    def crawl_ip3366(self):
        """
        获取代理 ip3366
        """
        BASE_URL2 = 'http://www.ip3366.net/free/?stype=1&page={page}'
        urls = [BASE_URL2.format(page=page) for page in range(1, 8)]
        for url in urls:
            logger.info(f'爬取 {url}')
            html = Crawler().fetch(url)
            if html:
                ip_address = re.compile('<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
                # \s * 匹配空格，起到换行作用
                re_ip_address = ip_address.findall(html)
                for address, port in re_ip_address:
                    proxy = Proxy(host=address.strip(), port=int(port.strip()))
                    yield proxy
 
    def crawl_iphai(self):
        """
        获取代理 iphai
        """
        BASE_URL3 = 'http://www.iphai.com/'
        html = Crawler().fetch(BASE_URL3)
        if html:
            find_tr = re.compile('<tr>(.*?)</tr>', re.S)
            trs = find_tr.findall(html)
            for s in range(1, len(trs)):
                find_ip = re.compile('<td>\s+(\d+\.\d+\.\d+\.\d+)\s+</td>', re.S)
                re_ip_address = find_ip.findall(trs[s])
                find_port = re.compile('<td>\s+(\d+)\s+</td>', re.S)
                re_port = find_port.findall(trs[s])
                for address, port in zip(re_ip_address, re_port):
                    proxy = Proxy(host=address.strip(), port=int(port.strip()))
                    yield proxy

    def crawl_kuaidaili(self):
        """
        获取代理 kuaidaili
        """
        BASE_URL4 = 'https://www.kuaidaili.com/free/inha/{page}/'
        urls = [BASE_URL4.format(page=page) for page in range(1, 200)]
        for url in urls:
            logger.info(f'爬取 {url}')
            html = Crawler().fetch(url)
            if html:
                doc = pq(html)
                for item in doc('table tr').items():
                    td_ip = item.find('td[data-title="IP"]').text()
                    td_port = item.find('td[data-title="PORT"]').text()
                    if td_ip and td_port:
                        yield Proxy(host=td_ip, port=td_port)