import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web
from jinja2 import Environment, FileSystemLoader

import orm
from coroweb import add_routes, add_static


# 编写处理函数
# def index(request):
#     只输入body不会显示任何文字，反而得到一个下载文件，所以加上content_type(内容类型HTTP请求头)
#     return web.Response(body=b'<h1>Awesome</h1>', content_type='text/html', charset='utf-8')

def init_jinja2(app, **kw):
	logging.info('init jinja2...')
	options = dict(
		# dict.get(key, default=None)
		# default——返回键不存在的情况下默认值，默认None
		autoescape=kw.get('autoescape', True),
		block_start_string=kw.get('block_start_string', '{%'),
		block_end_string=kw.get('block_end_string', '%}'),
		variable_start_string=kw.get('variable_start_string', '{{'),
		variable_end_string=kw.get('variable_end_string', '}}'),
		auto_reload=kw.get('auto_reload', True)
	)
	path = kw.get('path', None)
	if path is None:
		# os.path.join(path, name): 连接目录与文件名或目录
		# os.path.dirname(path): 返回文件路径
		# os.path.adspath(name): 获得绝对路径
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
	logging.info('set jinja2 template path: %s' % path)
	# 使用缺省配置创建了一个Environment实例，并指定FileSystemLoader作为模板加载器
	# 从path路径查找加载模板，
	env = Environment(loader=FileSystemLoader(path), **options)
	filters = kw.get('filters', None)
	if filters is not None:
		# dict.items() 返回可遍历的(键，值)元组数组
		for name, f in filters.items():
			env.filters[name] = f
	app['__templating__'] = env


# 在每个响应前打印日志
async def logger_factory(app, handler):
	async def logger(request):
		# request.method 表示提交请求使用的HTTP方法，大写。例（POST/GET）
		# request.path 表示提交请求页面完整地址的字符串，不包括域名
		logging.info('Request: %s %s' % (request.method, request.path))
		# await asyncio.sleep(0.3)
		return (await handler(request))

	return logger


async def data_factory(app, handler):
	# 解析数据
	async def parse_data(request):
		logging.info('data_factory...')
		# 处理POST请求
		if request.method == 'POST':
			# content_type 上传文件的内容类型
			# 判断content_type类型是否为JSON数据格式，如果是，需进行JSON数据交换处理
			# JSON (JavaScript Object Notation)为JavaScript原生格式，可以在其中被直接使用
			if request.content_type.startswith('application/json'):
				# request.json() 解码JSON数据
				request.__data__ = await request.json()
				if not isinstance(request.__data__, dict):
					return web.HTTPBadRequest(text='JSON body must be object.')
				logging.info('request json: %s' % str(request.__data__))
			elif request.content_type.startswith('application/x-www-form-urlencoded'):
				request.__data__ = await request.post()
				logging.info('request form: %s' % str(request.__data__))
			else:
				return web.HTTPBadRequest(text='Unsupported Content-Type: %s' % content_type)
		# 处理GET请求
		elif request.method == 'GET':
			# query_string 未解析的原始请求字符串
			qs = request.query_string
			request.__data__ = {k: v[0] for k, v in parse.parse_qs(qs, True).items()}
			logging.info('request query: %s' % request.__data__)
		else:
			request.__data__ = dict()
		return (await handler(request))
	return parse_data

# 将后端的返回值封装成浏览器可正确实现的Response对象
async def response_factory(app, handler):
	async def response(request):
		logging.info('Response handler...')
		r = await handler(request)
		if isinstance(r, web.StreamResponse):
			return r
		if isinstance(r, bytes):
			resp = web.Response(body=r)
			resp.content_type = 'application/octet-stream'
			return resp
		if isinstance(r, str):
			if r.startswith('redirect:'):
				return web.HTTPFound(r[9:])
			resp = web.Response(body=r.encode('utf-8'))
			resp.content_type = 'text/html;charset=utf-8'
			return resp
		if isinstance(r, dict):
			template = r.get('__template__')
			if template is None:
				resp = web.Response(body=json.dumps(r, ensure_ascii=False,
				                                    default=lambda o: o.__dict__).encode('utf-8'))
				resp.content_type = 'application/json;charset=utf-8'
				return resp
			else:
				#　浏览器响应是一个dict，body=test.html
				resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
				resp.content_type = 'text/html;charset=utf-8'
				return resp
		if isinstance(r, int) and r >= 100 and r < 600:
			return web.Response(r)
		if isinstance(r, tuple) and len(r) == 2:
			status, message = r
			if isinstance(status, int) and t >= 100 and t < 600:
				# status为状态码。 str(message)为附加信息
				return web.Response(status=status, text=str(message))
		# default:
		resp = web.Response(body=str(r).encode('utf-8'))
		resp.content_type = 'text/plain;charset=utf-8'
		return resp

	return response


def datetime_filter(t):
	delta = int(time.time() - t)
	if delta < 60:
		return u'1分钟前'
	if delta < 3600:
		return u'%s分钟前' % (delta // 60)
	if delta < 86400:
		return u'%s小时前' % (delta // 3600)
	if delta < 604800:
		return u'%s天前' % (delta // 86400)
	# 根据一个时间戳创建一个datatime对象
	dt = datetime.fromtimestamp(t)
	return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


# 创建web服务器,并将处理函数注册进其应用途径（Application.router)
async def init(loop):
	# Application, 构造函数def __init__(self,*,loop=None,...):
	# 通过orm来访问数据库
	await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='www-data', password='www-data', db='awesome')
	app = web.Application(loop=loop, middlewares=[
		logger_factory, response_factory])
	init_jinja2(app, filter=dict(datetime=datetime_filter))
	# handlers框架，处理带参数的URL
	add_routes(app, 'handlers')
	add_static(app)
	# router处理函数与对应的URL绑定，浏览器敲击URL是返回处理函数的内容
	# app.router.add_route('GET', '/', index)
	# 用协程创建监听服务，并使用aiohttp中的HTTP协议簇(protocol_factory)
	# srv, SocketServer
	srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
	# 打印日志，等级为info
	logging.info('server started at http://127.0.0.1:9000...')
	return srv


# 创建协程
loop = asyncio.get_event_loop()
# 运行协程，直到完成
loop.run_until_complete(init(loop))
# 运行协程，直到调用stop()
loop.run_forever()
