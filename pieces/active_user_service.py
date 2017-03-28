# coding=utf-8
import datetime
import time

import redis


class NotSetupException(Exception):
    def __init__(self):
        super(NotSetupException, self).__init__(u'RedisActiveUserService has not been setup.')


class RedisActiveUserService():
    """ 在线用户服务
    设置用户活跃, 获取活跃用户函数
    """
    ACTIVE_USERS_SET_CACHE_KEY = 'active_users_set'
    pool, redis, pipe, keep_secs = None, None, None, None

    BIG_LIMIT = 1000

    @classmethod
    def _check_setup(cls):
        if cls.pool and cls.redis and cls.pipe is not None:
            return
        raise NotSetupException()

    @classmethod
    def setup(cls, host, port=6379, password=None, db=0, keep_secs=60 * 5):
        """ 设置redis的host, post, 和db
        :param host: redis server ip 
        :param password: 密码
        :param port: 端口号
        :param db: 数据库号
        :param keep_secs: 活跃限制时长
        """
        port = port or 6379
        cls.pool = redis.ConnectionPool(host=host, port=port, password=password, db=db)
        cls.redis = redis.StrictRedis(connection_pool=cls.pool)
        cls.pipe = cls.redis.pipeline(transaction=False)
        cls.keep_secs = keep_secs or cls.keep_secs

    @classmethod
    def get_now_score(cls):
        """ 获取当前时间的时间戳, 作为当前时间的分值
        :return int: 
        """
        now = datetime.datetime.now()
        now_score = int(time.mktime(now.timetuple()))
        return now_score

    @classmethod
    def get_limit_score(cls, now_score=0):
        """ 获取相对当前时间, 失效的时间戳
        失效时间戳之前活跃的用户认为失活
        :param int now_score: 当前时间戳, 用以减少计算量
        :return int: 失效时间戳 
        """
        now_score = now_score or cls.get_now_score()
        limit_score = now_score - cls.keep_secs
        return limit_score

    @classmethod
    def active_user(cls, user):
        """ 激活用户
        :param str user: 用户标志
        """
        user = str(user)
        cls._check_setup()
        now_score = cls.get_now_score()
        limit_score = cls.get_limit_score(now_score)
        cls.pipe.zadd(cls.ACTIVE_USERS_SET_CACHE_KEY, **{user: now_score})
        cls.pipe.zremrangebyscore(cls.ACTIVE_USERS_SET_CACHE_KEY, 0, limit_score)
        cls.pipe.execute()

    @classmethod
    def get_active_users(cls):
        """ 获取激活的用户列表
        当活跃用户较少且需要一次做多次判定的时候推荐使用此方法获取用户是否活跃, 通过判定用户是否在返回的集合中, 
        当活跃用户数量比较庞大的时候不建议使用此方法, 请使用is_users_active.
        :return list[str]: 用户id列表
        """
        cls._check_setup()
        now_score = cls.get_now_score()
        limit_score = cls.get_limit_score(now_score)
        active_users = cls.redis.zrangebyscore(cls.ACTIVE_USERS_SET_CACHE_KEY, limit_score, now_score)
        return set(active_users)

    @classmethod
    def is_user_active(cls, user):
        """ 判定用户是否是活跃的
        当活跃用户较少且需要一次做多次判定的时候推荐使用get_active_users获取用户是否活跃, 通过判定用户是否在返回的集合中, 
        当活跃用户数量比较庞大的时候在使用此方法.
        :param users: 用户标志
        :return bool: 是否活跃
        """
        cls._check_setup()
        now_score = cls.get_now_score()
        limit_score = cls.get_limit_score(now_score)
        score = cls.redis.zscore(cls.ACTIVE_USERS_SET_CACHE_KEY, user)
        return bool(score and score > limit_score)

    @classmethod
    def is_users_active(cls, users):
        """ 获取多个用户是否活跃的结果
        :param users: 用户标志
        :return: users中活跃用户集合
        """
        cls._check_setup()
        # 当活跃用户量比较小
        if cls.redis.zcard(cls.ACTIVE_USERS_SET_CACHE_KEY) < cls.BIG_LIMIT:
            active_users = cls.get_active_users()
            return active_users.intersection(set(users))
        # 当活跃用户量比较大
        active_users = set()
        for user in users:
            if cls.is_user_active(user):
                active_users.add(user)
        return active_users


if __name__ == '__main__':
    RedisActiveUserService.setup('127.0.0.1')
    # for i in range(1500):
    #     RedisActiveUserService.active_user(str(i + 1000))
    print RedisActiveUserService.is_user_active('1440')
    print RedisActiveUserService.is_user_active('4000')
    print RedisActiveUserService.is_users_active(['1400', '1110001'])
    # print RedisActiveUserService.get_active_users()
