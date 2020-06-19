from flask import Flask, g
from proxypool.db import RedisClient
from proxypool.setting import API_HOST, API_PORT, API_THREADED


__all__ = ['app']

app = Flask(__name__)


def get_conn():
    """
    获取 Redis 对象
    """
    if not hasattr(g, 'redis'):
        g.redis = RedisClient()
    return g.redis

@app.route('/')
def index():
    return '<h2>Welcome to Proxy Pool System</h2>'

@app.route('/random')
def get_proxy():
    """
    获取随机代理
    """
    conn = get_conn()
    return conn.random().string()

@app.route('/count')
def get_count():
    """
    获取代理总量
    """
    conn = get_conn()
    return str(conn.count())


if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT, threaded=API_THREADED)