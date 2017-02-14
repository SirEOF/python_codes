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
    ACTIVE_KEEP_SECONDS = 60 * 5

    pool, conn, pipe = None, None, None

    @classmethod
    def _check_setup(cls):
        if cls.pool and cls.conn and cls.pipe is not None:
            return
        raise NotSetupException()

    @classmethod
    def setup(cls, host, port, db=0):
        """ 设置redis的host, post, 和db
        """
        cls.pool = redis.ConnectionPool(host='localhost', port=port, db=db)
        cls.conn = redis.StrictRedis(connection_pool=cls.pool)
        cls.pipe = cls.conn.pipeline(transaction=False)

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
        limit_score = now_score - cls.ACTIVE_KEEP_SECONDS
        return limit_score

    @classmethod
    def active_user(cls, user_id):
        """ 激活用户
        :param str user_id: 用户id
        """
        user_id = str(user_id)
        cls._check_setup()
        now_score = cls.get_now_score()
        limit_score = cls.get_limit_score(now_score)
        cls.pipe.zadd(cls.ACTIVE_USERS_SET_CACHE_KEY, **{user_id: now_score})
        cls.pipe.zremrangebyscore(cls.ACTIVE_USERS_SET_CACHE_KEY, 0, limit_score)
        cls.pipe.execute()

    @classmethod
    def get_active_users(cls):
        """ 获取激活的用户列表 
        :return list[str]: 用户id列表
        """
        cls._check_setup()
        now_score = cls.get_now_score()
        limit_score = cls.get_limit_score(now_score)
        active_users = cls.conn.zrangebyscore(cls.ACTIVE_USERS_SET_CACHE_KEY, limit_score, now_score)
        return active_users


if __name__ == '__main__':
    RedisActiveUserService.setup('localhost', 6379)
    RedisActiveUserService.active_user('2')
    print RedisActiveUserService.get_active_users()
