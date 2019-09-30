#!/usr/bin/env python3

import asyncio
import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import hashlib
from middlewares import authorize
import aiopg
from routes import routes
from settings import *

middle = [
    session_middleware(EncryptedCookieStorage(hashlib.sha256(bytes(SECRET_KEY, 'utf-8')).digest())),
#    authorize,
]

app = web.Application(middlewares=middle)

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

for route in routes:
    app.router.add_route(route[0], route[1], route[2], name=route[3])
app['static_root_url'] = '/static'
app.router.add_static('/static', 'static', name='static')

web.run_app(app)
