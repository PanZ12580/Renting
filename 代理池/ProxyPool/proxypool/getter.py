from loguru import logger
from proxypool.db import RedisClient
from proxypool.setting import PROXY_NUMBER_MAX
from proxypool.crawler import Crawler


class Getter(object):
    def __init__(self):
        """
        初始化数据库与爬虫
        """
        self.redis = RedisClient()
        self.crawler = Crawler()
    
    def is_full(self):
        """
        判断代理数目是否达上限
        """
        return self.redis.count() >= PROXY_NUMBER_MAX
    
    @logger.catch
    def run(self):
        logger.info('获取器开始执行......')
        if not self.is_full():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                proxies = self.crawler.get_proxies(callback)
                for proxy in proxies:
                    self.redis.add(proxy)


if __name__ == '__main__':
    getter = Getter()
    getter.run()