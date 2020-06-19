import redis
from proxypool.error import PoolEmptyException
from proxypool.utils import Proxy
from proxypool.setting import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_KEY, PROXY_SCORE_MAX, PROXY_SCORE_MIN, PROXY_SCORE_INIT
from random import choice
from typing import List
from loguru import logger
from proxypool.utils import is_valid_proxy, convert_proxy_or_proxies


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, **kwargs):
        """
        初始化 Redis 客户端
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True, **kwargs)
    
    def add(self, proxy: Proxy, score=PROXY_SCORE_INIT) -> int:
        """
        添加代理
        """
        if not is_valid_proxy(f'{proxy.host}:{proxy.port}'):
            logger.info(f'无效代理 {proxy}, 丢弃')
            return
        if not self.exists(proxy):
            return self.db.zadd(REDIS_KEY, {proxy.string(): score})
    
    def random(self) -> Proxy:
        """
        随机获取有效代理
        """
        # 尝试获取最高分数代理
        proxies = self.db.zrangebyscore(REDIS_KEY, PROXY_SCORE_MAX, PROXY_SCORE_MAX)
        if len(proxies):
            return convert_proxy_or_proxies(choice(proxies))
        # 如果不存在，按照排名获取
        proxies = self.db.zrevrange(REDIS_KEY, PROXY_SCORE_MIN, PROXY_SCORE_MAX)
        if len(proxies):
            return convert_proxy_or_proxies(choice(proxies))
        # 异常
        raise PoolEmptyException
    
    def decrease(self, proxy: Proxy) -> int:
        """
        代理值减一分，小于最小值则删除
        """
        score = self.db.zscore(REDIS_KEY, proxy.string())
        if score and score > PROXY_SCORE_MIN:
            logger.info(f'{proxy.string()} 当前分数为 {score}, 减 1')
            return self.db.zincrby(REDIS_KEY, -1, proxy.string())
        else:
            logger.info(f'{proxy.string()} 当前分数为 {score}, 移除')
            return self.db.zrem(REDIS_KEY, proxy.string())
    
    def exists(self, proxy: Proxy) -> bool:
        """
        判断是否存在
        """
        return not self.db.zscore(REDIS_KEY, proxy.string()) is None
    
    def max(self, proxy: Proxy) -> int:
        """
        将代理设置为MAX_SCORE
        """
        logger.info(f'{proxy.string()} 可用, 设置为 {PROXY_SCORE_MAX}')
        return self.db.zadd(REDIS_KEY, {proxy.string(): PROXY_SCORE_MAX})
    
    def count(self) -> int:
        """
        获取代理总量
        """
        return self.db.zcard(REDIS_KEY)
    
    def all(self) -> List[Proxy]:
        """
        获取全部代理
        """
        return convert_proxy_or_proxies(self.db.zrangebyscore(REDIS_KEY, PROXY_SCORE_MIN, PROXY_SCORE_MAX))
    
    def batch(self, start, end) -> List[Proxy]:
        """
        获取部分代理
        """
        return convert_proxy_or_proxies(self.db.zrevrange(REDIS_KEY, start, end - 1))


if __name__ == '__main__':
    conn = RedisClient()
    result = conn.random()
    print(result)