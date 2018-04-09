# -*- coding:utf-8 -*-
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from config import Config, configs
from flask import Flask
from flask_session import Session
import redis


# 创建可以被外界导入的数据库连接对象
db = SQLAlchemy()
# 创建可以被外界导入的连接到redis数据库的对象
redis_store = None


def get_app(config_name):

    app = Flask(__name__)

    # 1. 加载配置项, 根据进来的模式进行初始化配置
    app.config.from_object(configs[config_name])

    # 2. 创建连接到MySQL数据库的对象
    # db = SQLAlchemy(app)
    db.init_app(app)

    # 3. 创建连接到redis数据库的对象
    global redis_store
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    # 4. 开启csrf防护
    CSRFProtect(app)

    # 6.使用session在flask拓展实现将session数据存储在redis中
    Session(app)

    # 在app中注册蓝图
    from iHome.api_1_0 import api
    app.register_blueprint(api)

    return app
