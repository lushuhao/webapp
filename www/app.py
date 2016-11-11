import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

# 编写处理函数
def index(request):
	# 只输入body不会显示任何文字，反而得到一个下载文件，所以加上content_type(内容类型HTTP请求头)
	return web.Response(body=b'<h1>Awesome</h1>', content_type='text/html', charset='utf-8')

@asyncio.coroutine
# 创建web服务器,并将处理函数注册进其应用途径（Application.router)
def init(loop):
	# Application, 构造函数def __init__(self,*,loop=None,...):
	app = web.Application(loop=loop)
	# router处理函数与对应的URL绑定，浏览器敲击URL是返回处理函数的内容
	app.router.add_route('GET', '/', index)
	# 用协程创建监听服务，并使用aiohttp中的HTTP协议簇(protocol_factory)
	# srv, SocketServer
	srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
	# 打印日志，等级为info
	logging.info('server started at http://127.0.0.1:9000...')
	return srv

# 创建协程
loop = asyncio.get_event_loop()
# 运行协程，直到完成
loop.run_until_complete(init(loop))
# 运行协程，直到调用stop()
loop.run_forever()
