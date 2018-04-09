# -*- coding:utf-8 -*-
# 图片验证和短信验证码模块
from iHome.utils.captcha.captcha import captcha
from . import api


@api.route('/image_code')
def get_image_code():
    """提供图片验证码"""
    # 生成验证码:text是验证码的文字信息，image验证码的图片信息
    name, text, image = captcha.generate_captcha()

    # 响应验证码
    return image