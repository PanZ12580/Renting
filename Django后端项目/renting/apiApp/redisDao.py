from django.conf import settings

import redis
from random import choice


class RedisClient(object):
    def __init__(self, host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, **kwargs):
        """
        初始化 Redis 客户端
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True, **kwargs)
    
    def count(self):
        """
        获取代理总量
        """
        return self.db.zcard(settings.REDIS_KEY)
    
    def all(self, reverse):
        """
        获取全部代理，默认按分数升序
        """
        ls = self.db.zrange(settings.REDIS_KEY, 0, -1, withscores = True)
        col = ('proxy', 'score')
        proxyList = list(map(lambda x: dict(zip(col, x)), ls))
        res = sorted(proxyList, key = lambda x: x['score'], reverse = reverse)
        return res

    def remove(self, proxy):
        """
        删除指定代理
        """
        return self.db.zrem(settings.REDIS_KEY, *proxy)
    
