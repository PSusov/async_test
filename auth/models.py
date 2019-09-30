#!/usr/bin/env python3

import aiopg
import hashlib
from settings import PGCONF

class User():

    def __init__(self,data,**kw):
        self.login = data.get('login')
        if data.get('password'):
            self.password = hashlib.md5(data.get('password').encode()).hexdigest()
        self.id = data.get('id')

    async def get_user_id(self):
        async with aiopg.connect(PGCONF) as conn:
            cur = await conn.cursor()
            await cur.execute(f"SELECT id FROM users where login='{self.login}' and password='{self.password}'")
            result = await cur.fetchall()
            if len(result) > 0:
                return result[0][0]
            else:
                 return False

    async def get_login(self):
        async with aiopg.connect(PGCONF) as conn:
            cur = await conn.cursor()
            await cur.execute(f"SELECT login FROM users where id='{self.id}'")
            result = await cur.fetchone()
            if len(result) > 0:
                return result[0][0]
            else:
                 return False


    async def check_user(login):
        async with aiopg.connect(PGCONF) as conn:
            cur = await conn.cursor()
            await cur.execute(f"SELECT id FROM users where login='{login}'")
            ret = await cur.fetchall()
            if len(ret) > 0:
                return True
            else:
                 return False

    async def create_user(self):
        if not await User.check_user(self.login):
            async with aiopg.connect(PGCONF) as conn:
                cur = await conn.cursor()
                try:
                    await cur.execute(f"INSERT INTO users (login,password) VALUES ('{self.login}', '{self.password}') RETURNING id")
                    result = await cur.fetchone()
                    result = result[0]
                except Exception as err:
                    print(err)
                    result = f"Error creation user: {err}"
        else:
            result = "User exists"
        return result

    async def delete_user(self):
        async with aiopg.connect(PGCONF) as conn:
            cur = await conn.cursor()
            async with cur.begin():
                await cur.execute(f"DELETE from links where user_id='{self.id}'")
                await cur.execute(f"DELETE from users where id='{self.id}'")
                return True
            return False


    async def change_password(self,new_password):
        new_password = hashlib.md5(new_password.encode()).hexdigest()
        async with aiopg.connect(PGCONF) as conn:
            cur = await conn.cursor()
            try:
                await cur.execute(f"SELECT true FROM users WHERE id='{self.id}' and password='{self.password}'")
                if len(await cur.fetchall()) == 1:
                    await cur.execute(f"UPDATE users SET password='{new_password}' where id='{self.id}'")
                    result = "Password changed"
                else:
                    result = "Old password incorrect"
            except Exception as err:
                print(err)
                result = f"Error creation user: {err}"
            finally:
                return result

