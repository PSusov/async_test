#!/usr/bin/env python3

import json
from time import time
import aiohttp_jinja2
import aiopg
from aiohttp import web
from aiohttp_session import get_session
from auth.models import User

def redirect(request, router_name):
    url = request.app.router[router_name].url_for()
    raise web.HTTPFound(url)

def set_session(session, user_id, request):
    session['user'] = str(user_id)
    session['last_visit'] = time()
    redirect(request, 'main')

def convert_json(message):
    return json.dumps({'error': message})

class Login(web.View):

    @aiohttp_jinja2.template('auth/login.html')
    async def get(self):
        session = await get_session(self.request)
        if session.get('user'):
            redirect(self.request, 'main')
        return {'conten': 'Please enter login or email'}

    @aiohttp_jinja2.template('error.html')
    async def post(self):
        data = await self.request.post()
        user = User(data)
        result = await user.get_user_id()
        if result:
            session = await get_session(self.request)
            set_session(session, str(result), self.request)
        else:
            return {'error': 'incorrect login or password'}

class SignOff(web.View):
    async def get(self):
        session = await get_session(self.request)
        if session.get('user'):
            del session['user']
            redirect(self.request,'login')
        else:
            raise web.HTTPForbidden(body=b'Forbidden')

class ChangePass(web.View):

    @aiohttp_jinja2.template('auth/ch_pass.html')
    async def get(self):
        session = await get_session(self.request)
        if session.get('user'):
            return {}
        else:
            raise web.HTTPForbidden(body=b'Forbidden')

    @aiohttp_jinja2.template('auth/ch_pass.html')
    async def post(self):
        data = await self.request.post()
        session = await get_session(self.request)
        if session.get('user'):
            user = User({'password': data.get('password'), 'id': session.get('user')})
            new_password = data['new_password']
            retype_pass = data['retype_pass']
            form_error = []
            if len(new_password) < 6:
                form_error.append("Password too small")
            if new_password != retype_pass:
                form_error.append("Passwords not eq")
            if len(form_error) > 0:
                return {'form_error' : form_error }
            else:
                result = await user.change_password(new_password)
                return { 'result': result }
        else:
            return {'form_error' : ['Incorrect login or old password']}

class DeleteUser(web.View):

    @aiohttp_jinja2.template('auth/del_user.html')
    async def get(self):
        session = await get_session(self.request)
        if session.get('user'):
            user = User({'id': session.get('user')})
            login = await user.get_login()
            return {'login' : login }
        else:
            raise web.HTTPForbidden(body=b'Forbidden')

    @aiohttp_jinja2.template('auth/ch_pass.html')
    async def post(self):
        session = await get_session(self.request)
        if session.get('user'):
            user = User({'id': session.get('user')})
            result = await user.delete_user()
            if result:
                del session['user']
                redirect(self.request,'login')
            else:
                redirect(self.request,'main')
        else:
            raise web.HTTPForbidden(body=b'Forbidden')


class Register(web.View):

    @aiohttp_jinja2.template('auth/register.html')
    async def get(self):
        return {}

    @aiohttp_jinja2.template('auth/register.html')
    async def post(self):
        data = await self.request.post()
        login = data['login']
        password = data['password']
        retype_pass = data['retype_pass']
        form_error = []
        if len(login) < 3:
            form_error.append("Login too small")
        if await User.check_user(login):
            form_error.append("Login exists")
        if len(password) < 6:
            form_error.append("Password too small")
        if password != retype_pass:
            form_error.append("Passwords not eq")

        if len(form_error) > 0:
            return {'form_error' : form_error }
        else:
            user = User(data)
            result = await user.create_user()
            if isinstance(result,int):
                session = await get_session(self.request)
                set_session(session,str(result),self.request)
            else:
                return web.Response(content_type='application/json', text=convert_json(result))
