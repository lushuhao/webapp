'''
Models for user, blog, comment.
'''

import time, uuid

from orm import Model, StringField, BooleanField, FloatField, TextField

def next_id():
	# '%015d' 用0补充位置使%d和前方0一共15位
	# time.time() 返回当前时间戳
	# 时间戳是指格林威治时间1970年1月1日00:00:00起至现在的总秒数
	# uuid 是128位的全局唯一标识符，通常由32字节的字符串表示。uuid4()——基于随机数，hex十六进制
	return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
	__table__ = 'users'

	# 主键id的缺省值是函数next_id （缺省值就是默认值。是指一个属性、参数在被修改前的初始值）
	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	email = StringField(ddl='varchar(50)')
	passwd = StringField(ddl='varchar(50)')
	admin = BooleanField()
	name = StringField(ddl='varchar(50)')
	image = StringField(ddl='varchar(500)')
	# 创建时间created_at的缺省值是函数time.time，可以自动设置当前日期和时间
	# 日期和时间用float类型存储在数据库中，而不是datetime类型，这么做的好处
	# 是不必关心数据库的时区以及时区转换问题，排序非常简单，显示的时候，
	# 只需要做一个float到str的转换，也非常容易
	created_at = FloatField(default=time.time)

class Blog(Model):
	__table__ = 'blogs'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	user_name = StringField(ddl='varchar(50)')
	user_image = StringField(ddl='varchar(500)')
	name = StringField(ddl='varchar(50)')
	summary = StringField(ddl='varchar(200)')
	content = TextField()
	created_at = FloatField(default=time.time)

class Comment(Model):
	__table__ = 'comments'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	blog_id = StringField(ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	user_name = StringField(ddl='varchar(50)')
	user_image = StringField(ddl='varchar(500)')
	content = TextField()
	created_at = FloatField(default=time.time)
