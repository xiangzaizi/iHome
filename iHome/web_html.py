# -*- coding:utf-8 -*-
from flask import Blueprint, current_app,make_response


# 创建蓝图
from flask_wtf.csrf import generate_csrf

html_blue = Blueprint('html_blue', __name__)


# 使用蓝图
@html_blue.route('/<re(".*"):file_name>')
# @html_blue.route('/<file_name>')
def get_static_html(file_name):
    """获取静态文件"""
    # 需求: http://127.0.0.1:5000/login.html
    # 拼接file_name所有路径: '/static/html/login.html'
    # flask默认加载文件路径: '/static/html/login.html'
    # static_file = 'static'
    # 默认路由/, 首页
    if not file_name:
        file_name = 'index.html'

    # http://127.0.0.1:5000/favicon.ico
    # 这样ico不能进来就直接return拼接了->http://127.0.0.1:5000/favicon.ico
    if file_name != 'favicon.ico':
        file_name = 'html/' + file_name

    # return current_app.send_static_file(file_path)
    # file_path= u'/html/api/1.0/index.html'

    # 获取response
    response = make_response(current_app.send_static_file(file_name))
    token = generate_csrf()

    # 将csrf_token数据写入到cookie中
    response.set_cookie('csrf_token', token)


    # 查找指定路径下的静态页面的时候, 在cookie中设置csrf_token
    # return current_app.send_static_file(file_name)
    return response

