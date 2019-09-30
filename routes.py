#!/usr/bin/env python3

from auth.views import Login,Register,SignOff,ChangePass,DeleteUser
from main.views import Main


routes = [
    ('GET','/',Login,'login'),
    ('POST','/login',Login,'login_check'),
    ('*','/register',Register,'register'),
    ('*', '/signoff', SignOff, 'signoff'),
    ('*', '/ch_pass', ChangePass, 'ch_pass'),
    ('*', '/del_user', DeleteUser, 'del_user'),
    ('GET','/main',Main,'main'),
    ('POST','/link_add',LinkAdd,'link_add'),

]