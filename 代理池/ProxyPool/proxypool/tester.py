import asyncio
import aiohttp
from loguru import logger
from proxypool.utils import Proxy
from proxypool.db import RedisClient
from proxypool.setting import TEST_TIMEOUT, TEST_BATCH, TEST_URL, TEST_VALID_STATUS
from aiohttp import ClientProxyConnectionError, ServerDisconnectedError, ClientOSError, ClientHttpProxyError
from asyncio import TimeoutError


EXCEPTIONS = (
    ClientProxyConnectionError,
    ConnectionRefusedError,
    TimeoutError,
    ServerDisconnectedError,
    ClientOSError,
    ClientHttpProxyError
)


class Tester(object):
    def __init__(self):
        """
        初始化 Redis
        """
        self.redis = RedisClient()
        self.loop = asyncio.get_event_loop()
    
    async def test(self, proxy: Proxy):
        """
        测试单个代理:
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                logger.debug(f'测试 {proxy.string()}')
                async with session.get(TEST_URL, proxy=f'http://{proxy.string()}', timeout=TEST_TIMEOUT,
                                       allow_redirects=False) as response:
                    if response.status in TEST_VALID_STATUS:
                        self.redis.max(proxy)
                        logger.debug(f'代理 {proxy.string()} 可用, 加分')
                    else:
                        self.redis.decrease(proxy)
                        logger.debug(f'代理 {proxy.string()} 无效, 减分')
            except EXCEPTIONS:
                self.redis.decrease(proxy)
                logger.debug(f'代理 {proxy.string()} 无效, 减分')
    
    def run(self):
        """
        测试主函数
        """
        logger.info('启动测试器......')
        count = self.redis.count()
        logger.debug(f'{count} 个代理等待测试')
        
        for i in range(0, count, TEST_BATCH):
            # 开始测试的代理，停止测试的代理
            start, end = i, min(i + TEST_BATCH, count)
            logger.debug(f'测试索引值从 {start} 到 {end} 的代理')
            proxies = self.redis.batch(start, end)
            tasks = [self.test(proxy) for proxy in proxies]
            # 使用事件循环运行任务
            self.loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    tester = Tester()
    tester.run()