# -*- coding:utf-8 -*-
# 处理订单逻辑


from . import api
from iHome.utils.common import login_required
from flask import request,jsonify,current_app,g
from iHome.utils.response_code import RET
import datetime
from iHome.models import House,Order
from iHome import db


@api.route('/orders/<int:order_id>/comment', methods=['POST'])
@login_required
def set_order_comment(order_id):
    """发表评价
    0.判断用户是否登录
    1.接受参数：order_id，comment，判断是否为空
    2.查询要评价的订单
    3.设置评价信息，修改订单状态
    4.保存到数据库
    5.响应结果
    """

    # 1.接受参数：order_id，comment，判断是否为空
    comment = request.json.get('comment')
    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 2.查询要评价的订单
    try:
        order = Order.query.filter(Order.id==order_id,Order.user_id==g.user_id,Order.status=='WAIT_COMMENT').first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询订单数据失败')
    if not order:
        return jsonify(errno=RET.NODATA, errmsg='订单不存在')

    # 3.设置评价信息，修改订单状态
    order.comment = comment
    order.status = 'COMPLETE'

    # 4.更新数据到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存评价信息失败')

    # 5.响应结果
    return jsonify(errno=RET.OK, errmsg='OK')


@api.route('/orders/<int:order_id>', methods=['PUT'])
@login_required
def set_order_status(order_id):
    """确认订单
    0.判断是否登录
    1.查询order_id对应的订单信息
    2.判断当前登录使用是否是该订单的房东
    3.修改订单的status属性为"已接单"
    4.更新数据到数据库
    5.响应结果
    """

    # 获取action
    action = request.args.get('action')
    if action not in ['accept', 'reject']:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 1.查询order_id对应的订单信息
    try:
        order = Order.query.filter(Order.id==order_id, Order.status=='WAIT_ACCEPT').first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询订单数据失败')
    if not order:
        return jsonify(errno=RET.NODATA, errmsg='订单不存在')

    # 2.判断当前登录用户是否是该订单的房东
    login_user_id = g.user_id
    landlord_user_id = order.house.user_id
    if login_user_id != landlord_user_id:
        return jsonify(errno=RET.USERERR, errmsg='权限不够')

    # 3.修改订单的status属性为"已接单"
    if action == 'accept':
        order.status = 'WAIT_COMMENT'
    else:
        order.status = 'REJECTED'
        # 保存拒单理由
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg='缺少拒单理由')
        order.comment = reason # 一旦被拒单，就无法评价，可以使用一个字段复用

    # 4.更新数据到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存订单状态失败')

    # 5.响应结果
    return jsonify(errno=RET.OK, errmsg='OK')


@api.route('/orders')
@login_required
def get_order_list():
    """获取我的订单
    0.判断是否登录
    1.获取参数：user_id = g.user_id
    2.查询该登录用户的所有的订单信息
    3.构造响应数据
    4.响应结果
    """

    # 获取用户身份信息
    role = request.args.get('role')
    if role not in ['custom', 'landlord']:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少必传参数')

    # 1.获取参数：user_id = g.user_id
    user_id = g.user_id

    # 2.查询该登录用户的所有的订单信息
    try:
        if role == 'custom':
            orders = Order.query.filter(Order.user_id==user_id).all()
        else:
            # 查询该登录用户发布的房屋信息
            houses = House.query.filter(House.user_id==user_id).all()
            # 获取发布的房屋的ids
            house_ids = [house.id for house in houses]
            # 从订单中查询出订单中的house_id在house_ids
            orders = Order.query.filter(Order.house_id.in_(house_ids)).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询订单失败')

    # 3.构造响应数据
    order_dict_list = []
    for order in orders:
        order_dict_list.append(order.to_dict())

    # 4.响应结果
    return jsonify(errno=RET.OK, errmsg='OK',data=order_dict_list)


@api.route('/orders', methods=['POST'])
@login_required
def create_order():
    """创建、提交订单
    0.判断用户是否登录
    1.接受参数，house_id, 入住时间和离开时间
    2.校验参数，判断入住时间和离开是否符合逻辑，校验房屋是否存在
    3.判断当前房屋有没有被预定
    4.创建订单模型对象，并存储订单数据
    5.保存到数据库
    6.响应结果
    """

    # 1.接受参数，house_id, 入住时间和离开时间
    json_dict = request.json
    house_id = json_dict.get('house_id')
    start_date_str = json_dict.get('start_date')
    end_date_str = json_dict.get('end_date')
    # 判断是否缺少参数
    if not all([house_id,start_date_str,end_date_str]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 2.校验参数，判断入住时间和离开是否符合逻辑，校验房屋是否存在
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        # 自己校验入住时间是否小于离开的时间
        if start_date and end_date:
            # 断言：入住时间一定小于离开时间，如果不满足，就抛出异常
            assert start_date < end_date, Exception('入住时间有误')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='入住时间有误')

    # 判断房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 3.判断当前房屋有没有被预定
    try:
        conflict_orders = Order.query.filter(Order.house_id==house_id,end_date > Order.begin_date, start_date < Order.end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询冲突订单失败')
    # 如果有值，说明要预订的房屋在该时间节点，已经在订单中，说明被预定
    if conflict_orders:
        return jsonify(errno=RET.DATAERR, errmsg='房屋已被预订')

    # 4.创建订单模型对象，并存储订单数据
    days = (end_date-start_date).days # 计算时间段之间的天数
    order = Order()
    order.user_id = g.user_id
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = days
    order.house_price = house.price
    order.amount = house.price * days

    # 5.保存到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存订单数据失败')

    # 6.响应结果
    return jsonify(errno=RET.OK, errmsg='OK')