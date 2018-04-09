# -*- coding:utf-8 -*-
import logging
import redis


class Config(object):

    # 1. 开启Debug模式, 仅在调试模式时
    DEBUG = True
    # 配合csrf_toke生成密钥信息
    SECRET_KEY = '2bnoqMGo0skFfDzcBEwybltcJ9VQi0XX7bsGk5HtlSlnlOemC7UE48LNGeGgJ5EQ'

    # 2. 配置MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. 配置redis数据库,
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = '6379'

    # 4. 配置session数据存储到redis数据库中

    # 关于类型的选择在from flask_session import Session
    # 查看Session中源代码可以看到session的存储可以选择各种类型的数据库
    SESSION_TYPE = 'redis'
    # 指定存储session数据的redis位置
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 开启session数据的签名, 这样session数据将以密文的形式存储
    SESSION_USE_SIGNER = True
    # 设置session的会话的超时时长: 一天
    PERMANENT_SESSION_LIFETIME = 3600*24


"""配置可选择的测试模式"""
class DevelopmentConfig(Config):
    """创建调试环境下的配置类"""
    # 我们的爱家租房的房型，调试模式的配置和Config一致，所以pass

    # 开发环境中日志等级设置为DEBUG
    LOGGING_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """创建线上环境下的配置类"""

    # 重写有差异性的配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@192.168.72.77:3306/iHome'


class UnittestConfig(Config):
    """单元测试的配置"""

    # 重写有差异性的配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_unittest'


# 准备工厂设计模式的原材料
configs = {
    'default_config': Config,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'unittest': UnittestConfig
}






