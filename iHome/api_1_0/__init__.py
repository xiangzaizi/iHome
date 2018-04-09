# -*- coding:utf-8 -*-
from flask import Blueprint

# RESTFUL 设计模式
# 提示: 一个接口版本里面需要一个蓝图, 并指定版本唯一标识
api = Blueprint('api_1_0', __name__, url_prefix='/api/1.0')

# 将蓝图注册的路由一并导入, 为视图和路由之间建立关系