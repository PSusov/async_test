#!/usr/bin/env python3

import json
from time import time
import aiohttp_jinja2
import aiopg
from aiohttp import web
from aiohttp_session import get_session
from main.models import Link

def redirect(request, router_name):
    url = request.app.router[router_name].url_for()
    raise web.HTTPFound(url)

def convert_json(message):
    return json.dumps({'error': message})

class Main(web.View):

    @aiohttp_jinja2.template('main/main.html')
    async def get(self):
        session = await get_session(self.request)
        if session.get('user'):
            link = Link({'user_id': session.get('user')})
            result = await link.link_list()
            return {'links' : result }
        else:
            redirect(self.request,'login')

    async def post(self):
        data = await self.request.post()
        user = User(data)
        result = await user.check_user()
        if result:
            session = await get_session(self.request)
            set_session(session, str(result), self.request)
        else:
            return web.Response(content_type='application/json', text=convert_json(result))

class LinkAdd(web.View):
    
    @aiohttp_jinja2.template('error.html')
    async def post(self):
        data = await self.request.post()
        session = await get_session(self.request)
        user_id = session.get('user')
        if user_id:
            link = Link({'link': data.get('link'),'user_id': user_id})
            result = await link.add_link()
            if isinstance(result,str):
                return { 'error' : result }
            else:
                redirect(self.request,'main')