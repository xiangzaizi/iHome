# -*- coding:utf-8 -*-
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from config import Config, configs
from flask import Flask
from flask_session import Session
import redis
from iHome.utils.common import RegexConverter
import logging
from logging.handlers import RotatingFileHandler


# 创建可以被外界导入的数据库连接对象
db = SQLAlchemy()
# 创建可以被外界导入的连接到redis数据库的对象
redis_store = None


# 在业务逻辑一开始就开启日志
def setupLogging(level):
    """
    如果是开发模式，'development' -> 'DEBUG'
    如果是生产模式， 'production' -> 'WARN'
    """
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def get_app(config_name):

    # 调用封装的日志
    setupLogging(configs[config_name].LOGGING_LEVEL)

    app = Flask(__name__)

    # 1. 加载配置项, 根据进来的模式进行初始化配置
    app.config.from_object(configs[config_name])

    # 2. 创建连接到MySQL数据库的对象
    # db = SQLAlchemy(app)
    db.init_app(app)

    # 3. 创建连接到redis数据库的对象
    global redis_store
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    # 4. 开启CSRFf防护
    CSRFProtect(app)

    # 6.使用session在flask拓展实现将session数据存储在redis中
    Session(app)

    # 导入自定义的路由转换器
    app.url_map.converters['re'] = RegexConverter


    # 在app中注册蓝图
    from iHome.api_1_0 import api
    app.register_blueprint(api)

    # 静态页面访问的注册
    from iHome.web_html import html_blue
    app.register_blueprint(html_blue)

    return app
