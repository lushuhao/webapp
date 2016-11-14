import re, time, json, logging, hashlib, base64, asyncio

from coroweb import get, post

from models import User, Comment, Blog, next_id

@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',    # 指定的模板文件是'test.html',位于根目录templates
        'users': users    # 其他参数是传递给模板的数据
}