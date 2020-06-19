import platform
from os.path import dirname, abspath, join
from environs import Env
from loguru import logger
from proxypool.utils import parse_redis_connection_string


env = Env()
# 读取环境变量
env.read_env()

IS_WINDOWS = platform.system().lower() == 'windows'

ROOT_DIR = dirname(dirname(abspath(__file__)))
LOG_DIR = join(ROOT_DIR, env.str('LOG_DIR', 'logs'))

# 定义环境
DEV_MODE, TEST_MODE, PROD_MODE = 'dev', 'test', 'prod'
APP_ENV = env.str('APP_ENV', DEV_MODE).lower()
APP_DEBUG = env.bool('APP_DEBUG', True if APP_ENV == DEV_MODE else False)
APP_DEV = IS_DEV = APP_ENV == DEV_MODE
APP_PROD = IS_PROD = APP_ENV == PROD_MODE
APP_TEST = IS_TEST = APP_ENV == TEST_MODE

# Redis 数据库地址
REDIS_HOST = env.str('REDIS_HOST', '127.0.0.1')

# Redis 端口
REDIS_PORT = env.int('REDIS_PORT', 6379)

# Redis 密码，如无填写“None”
REDIS_PASSWORD = env.str('REDIS_PASSWORD', "")

# Redis 连接字符串
REDIS_CONNECTION_STRING = env.str('REDIS_CONNECTION_STRING', None)

if REDIS_CONNECTION_STRING:
    REDIS_HOST, REDIS_PORT, REDIS_PASSWORD = parse_redis_connection_string(REDIS_CONNECTION_STRING)

REDIS_KEY = env.str('REDIS_KEY', 'proxies:universal')

# 代理分数
PROXY_SCORE_MAX = 100
PROXY_SCORE_MIN = 0
PROXY_SCORE_INIT = 10

# 代理总数的阈值
PROXY_NUMBER_MAX = 50000
PROXY_NUMBER_MIN = 0

# 检查周期
CYCLE_TESTER = env.int('CYCLE_TESTER', 20)

# 获取周期
CYCLE_GETTER = env.int('CYCLE_GETTER', 100)

# 测试API
TEST_URL = env.str('TEST_URL', 'https://sh.lianjia.com/zufang')
TEST_TIMEOUT = env.int('TEST_TIMEOUT', 10)
TEST_BATCH = env.int('TEST_BATCH', 20)
TEST_VALID_STATUS = env.list('TEST_VALID_STATUS', [200, 206, 302])

# API配置
API_HOST = env.str('API_HOST', '0.0.0.0')
API_PORT = env.int('API_PORT', 5555)
API_THREADED = env.bool('API_THREADED', True)

# 开关
ENABLE_TESTER = env.bool('ENABLE_TESTER', True)
ENABLE_GETTER = env.bool('ENABLE_GETTER', True)
ENABLE_SERVER = env.bool('ENABLE_SERVER', True)

logger.add(env.str('LOG_RUNTIME_FILE', 'runtime.log'), level='DEBUG', rotation='1 week', retention='20 days')
logger.add(env.str('LOG_ERROR_FILE', 'error.log'), level='ERROR', rotation='1 week')