import json

from redis import Redis

from configurations import config


class RedisQueue(object):
    """
    redis 队列封装
    todo 链接信息配置 广播 其他操作等
    """

    def __init__(self, name, namespace=config.get("asx", "house_name")):
        """
        redis_kwargs: 连接信息
        """
        self.__db = Redis(host=config.get("redis", "host"),
                          port=config.get("redis", "port"),
                          db=config.get("queue", "redis_db"))
        self.key = '%s:%s' % (namespace, name)

    def size(self):
        return self.__db.llen(self.key)

    def is_empty(self):
        return self.size() == 0

    def put(self, item):
        """
        支持dict直接put
        """
        if isinstance(item, dict):
            item = json.dumps(item)
        self.__db.rpush(self.key, item)

    def get_with_block_mode(self, is_dict_mode=False, timeout=0):
        """
        阻塞模式，如果队列为空，会一直等待，直到timeout
        获取队列中第一条数据
        is_dict_mode: 是否需要自动load json
        timeout: 超时时间
        """
        item = self.__db.blpop(self.key, timeout=timeout)
        if item:
            # 0是key，1是value
            item = item[1]

        if is_dict_mode:
            try:
                return json.loads(item)
            except:
                return item
        else:
            return item

    def get(self, is_dict_mode=False):
        """
        is_dict_mode: 是否需要自动load json
        """
        item = self.__db.lpop(self.key)

        if is_dict_mode:
            try:
                return json.loads(item)
            except:
                return item
        else:
            return item

    def pub(self, channel, msg):
        return self.__db.publish(channel, msg)

    def listen(self, channel):
        p = self.__db.pubsub()
        p.subscribe(channel)
        return p.listen()
