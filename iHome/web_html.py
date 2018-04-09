# -*- coding:utf-8 -*-
from flask import Blueprint


# 创建蓝图
from flask import current_app

html_blue = Blueprint('html_blue', __name__)


# 使用蓝图
@html_blue.route('/<re(".*"):file_name>')
def get_static_html(file_name):
    """获取静态文件"""
    # 需求: http://127.0.0.1:5000/login.html
    # 拼接file_name所有路径: '/static/html/login.html'
    # flask默认加载文件路径: '/static/html/login.html'
    # static_file = 'static'

    if not file_name:
        file_name = 'index.html'

    file_path = 'html/' + file_name

    return current_app.send_static_file(file_path)

