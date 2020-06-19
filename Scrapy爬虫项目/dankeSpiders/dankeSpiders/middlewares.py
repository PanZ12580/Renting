# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests

class DankespidersSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class DankespidersDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        Cookie = 'sajssdk_2015_cross_new_user=1; Hm_lvt_814ef98ed9fc41dfe57d70d8a496561d=1592359944; UM_distinctid=172c00c817b543-044baba80d6eaa-143f6256-1aeaa0-172c00c817ca64; CNZZDATA1271579284=139643172-1592354910-https%253A%252F%252Fwww.danke.com%252F%7C1592360311; XSRF-TOKEN=eyJpdiI6IlNNMko2VVBOWjU1OEphQWFKdjFsUmc9PSIsInZhbHVlIjoib3dYTnJGTSttZjhrZ3JnK2d5eXlhZ2dRc1hGait3dDltMU94ekNZRjM1ZVFQakhnXC9CRjZWeUpVVVRjN3JZSUxpNmxsdDExWkFhNFpiQU5XVVFqQjZ3PT0iLCJtYWMiOiI5NjZhM2UzZWM0NGNmZjk5MmUwYTQ5ZGFiMzQ2NmMwNWNmNDY3ZWEwYjBiYzViODMwZjM2NDU0MWI4NWVjNGU2In0%3D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22172c00c443cb0b-010a9e7c4c842b-143f6256-1764000-172c00c443d270%22%2C%22%24device_id%22%3A%22172c00c443cb0b-010a9e7c4c842b-143f6256-1764000-172c00c443d270%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%2C%22%24latest_referrer_host%22%3A%22www.baidu.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22platformType%22%3A%22PC%22%2C%22pid%22%3A%22dankegongyu_customer%22%2C%22cid%22%3A%22sh%22%2C%22ucid%22%3A%22%22%2C%22uuid%22%3A%22%22%2C%22ssid%22%3A%22%22%2C%22lmei%22%3A%22%22%2C%22android_id%22%3A%22%22%2C%22idfa%22%3A%22%22%2C%22idfv%22%3A%22%22%2C%22mac_id%22%3A%22%22%2C%22%24url%22%3A%22https%3A%2F%2Fwww.danke.com%2Fsh%22%7D%7D; Hm_lpvt_814ef98ed9fc41dfe57d70d8a496561d=1592361520; session=eyJpdiI6ImpsTmsxbGtQc1M2TXZOYTd0RFF5dnc9PSIsInZhbHVlIjoiTkZRNkplSytqdXlRY1wvRTJCWndNQjdoZVJ2cGJ4VWVsZHpQZEVKaEVqZEliYThUZWVzb1lRamZHd3k3RHZHTWh0U0k1cTlxOSt1Y0tVUjQ1WHFCc01RPT0iLCJtYWMiOiJhNWMyNDc5MTE3NWI0YzA2Nzg5YTE4ZWZmNDJjYzVmZDkyMDI0YjY3NWUxM2EzNjM3ZTc1MDhlNDk4Y2JlNWFmIn0%3D'
        self.cookies = {i.split("=")[0]: i.split("=")[1] for i in Cookie.split("; ")}

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        # 设置cookie
        request.cookies = self.cookies
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        # 更新cookie
        cookies = response.headers.getlist('Set-Cookie')
        for cookie in cookies:
            c = str(cookie).split(";")[0].split("=")
            self.cookies[c[0]] = c[1]
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class ProxyMiddleware():
    def __init__(self, proxy_url):
        self.proxy_url = proxy_url
    
    def get_random_proxy(self):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code == 200:
                proxy = response.text
                return proxy
        except requests.ConnectionError:
            return False
    
    def process_request(self, request, spider):
        if request.meta.get('retry_times'):
            proxy = self.get_random_proxy()
            if proxy:
                uri = 'https://{proxy}'.format(proxy=proxy)
                print('使用代理 ' + proxy)
                request.meta['proxy'] = uri

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            proxy_url=settings.get('PROXY_URL')
        )
