class PoolEmptyException(Exception):
    def __str__(self):
        return repr('代理池已经枯竭')
    
    def __init__(self):
        Exception.__init__(self)