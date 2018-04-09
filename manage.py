# -*- coding:utf-8 -*-
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from iHome import get_app, db


# 创建app
app = get_app('development')


# 5. 创建脚本管理器对象
manager = Manager(app)

# 数据库与应用之间建立关联
Migrate(app, db)
# 将数据库迁移脚本添加到脚本管理器中
manager.add_command('db', MigrateCommand)




if __name__ == '__main__':
    print app.url_map
    # app.run(debug=True)
    manager.run()
