import json

from rejson import Client, Path

from configurations import config


class RedisClient(object):
    def __init__(self, db=config.get("queue", "redis_db"), host=config.get("redis", "host"),
                 port=config.get("redis", "port"),
                 username=config.get("redis", "user"), password=config.get("redis", "pass")):

        self.rejson_client = Client(
            host=host,
            port=str(port),
            db=db,
            username=username,
            password=password,
            decode_responses=True
        )
        self.house_name = f'{config.get("house", "house_name")}:'

    def json_set(self, objname=None, objdict=None, ex=None):

        objname = f"{self.house_name}:{objname}"

        self.rejson_client.jsonset(objname, Path.rootPath(), objdict)
        if ex:
            self.rejson_client.expire(objname, ex)

    def json_get(self, key, path='.'):

        if ":" not in key:
            key = f"{self.house_name}:{key}"
        if path.strip() == '.':
            return self.rejson_client.jsonget(key, Path.rootPath())
        else:
            return self.rejson_client.jsonget(key, Path(path))

    def set_kv(self, key, value, ex=None):
        key = f"{self.house_name}{key}"
        if isinstance(value, dict):
            value = json.dumps(value)
        self.rejson_client.set(key, value)
        if ex:
            self.rejson_client.expire(key, ex)

    def get(self, key):
        key = f"{self.house_name}{key}"
        data = self.rejson_client.get(key)
        try:
            if isinstance(key, str):
                data = json.loads(data)
        except Exception as e:
            print(e)
        return data

    def l_push(self, key, *args, repeat=False):
        """
        将一个或多个值插入到列表头部
        例: 将 [1,2,3] 插入队列
        3 -> 2 -> 1
        队列从右边取调用r_pop方法
        堆栈从左边取调用l_pop方法

        :param repeat: repeat为True则不支持将重复数据加入到队列里
        :param key: 队列的名称
        :param args: 加入队列的数据
        :return: 队列里的排队序号
        """
        key = f"{self.house_name}{key}"
        value_args = []
        if repeat:
            values = self.lrange(key)
            for value in args:
                if value in values:
                    raise Exception("There is duplicate data in the queue.")
                else:
                    value_args.append(json.dumps(value))
        else:
            value_args = [json.dumps(value) for value in args]
        return self.rejson_client.lpush(key, *value_args)

    def r_pop(self, key):
        """
        移出并获取列表的最后一个元素， 如果列表没有元素会阻塞列表直到等待超时或发现可弹出元素为止。
        先进先出，适用于队列
        :param key:
        :return: 移除的元素
        """
        key = f"{self.house_name}{key}"
        data = self.rejson_client.brpop(key)
        try:
            return json.loads(data[1] if data else None)
        except Exception as e:
            return data

    def l_pop(self, key):
        """
        移出并获取列表的第一个元素， 如果列表没有元素会阻塞列表直到等待超时或发现可弹出元素为止。
        后进先出，适用于堆栈
        :param key:
        :return: 移除的元素
        """
        key = f"{self.house_name}:{key}"
        data = self.rejson_client.brpop(key)
        try:
            return json.loads(data[1] if data else None)
        except Exception as e:
            return data

    def lrange(self, key, start=0, stop=-1):
        """
        获取列表指定范围内的元素
        :param key:
        :param start:
        :param stop:
        :return:获取列表指定范围内的元素
        """
        key = f"{self.house_name}{key}"
        return [json.loads(value) for value in self.rejson_client.lrange(key, start, stop)]

    def type(self, key):
        key = f"{self.house_name}{key}"
        return self.rejson_client.type(key)

    def keys(self, pattern='*'):
        lst = self.rejson_client.keys(pattern=pattern)
        # for i, d in enumerate(lst):
        #     lst[i] = d.decode()
        return lst


if __name__ == '__main__':
    redis_client = RedisClient()
    redis_client.house_name = "test"
    # redis_client.json_set("qwq123", {"123": "123"})
    print(redis_client.json_get("crawl_taobao::730883376648"))
    # print(redis_client.json_get("crawl_taobao*"))
    print(len(redis_client.keys("crawl_taobao*")))
    # for i in range(5):
    #     ...
    #     print(redis_client.l_push("asx_data1", str(i)))
    #     # print(redis_client.r_pop("asx_data1"))
