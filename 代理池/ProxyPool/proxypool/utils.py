import re
from attr import attrs, attr


@attrs
class Proxy(object):
    host = attr(type=str, default=None)
    port = attr(type=int, default=None)
    
    def __str__(self):
        return f'{self.host}:{self.port}'
    
    def string(self):
        return self.__str__()

if __name__ == '__main__':
    proxy = Proxy(host='8.8.8.8', port=8888)
    print('proxy', proxy)
    print('proxy', proxy.string())


def is_valid_proxy(data):
    return re.match('\d+\.\d+\.\d+\.\d+\:\d+', data)

def convert_proxy_or_proxies(data):
    if not data:
        return None
    if isinstance(data, list):
        result = []
        for item in data:
            # skip invalid item
            item = item.strip()
            if not is_valid_proxy(item): continue
            host, port = item.split(':')
            result.append(Proxy(host=host, port=int(port)))
        return result
    if isinstance(data, str) and is_valid_proxy(data):
        host, port = data.split(':')
        return Proxy(host=host, port=int(port))

def parse_redis_connection_string(connection_string):
    result = re.match('rediss?:\/\/(.*?)@(.*?):(\d+)', connection_string)
    return result.group(2), int(result.group(3)), (result.group(1) or None) if result \
        else ('localhost', 6379, None)