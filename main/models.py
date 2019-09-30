#!/usr/bin/env python3

import aiopg
from settings import PGCONF

class Link():


    def __init__(self,data,**kw):
        self.link = data.get('link')
        self.user_id = data.get('user_id')

    async def check_link(self):
        async with aiopg.connect(PGCONF) as conn:
            cur = await conn.cursor()
            await cur.execute(f"SELECT id FROM links where user_id='{self.user_id}' and link='{self.link}'")
            ret = await cur.fetchall()
            if len(ret) > 0:
                return ret[0][0]
            else:
                 return False

    async def add_link(self):
        if not await self.check_link():
            async with aiopg.connect(PGCONF) as conn:
                cur = await conn.cursor()
                try:
                    await cur.execute(f"INSERT INTO links (user_id,link) VALUES ('{self.user_id}','{self.link}')")
                    return True
                except Exception as err:
                    return f"Error adding link: {err}"
        else:
            return "Link exists"

    async def link_list(self):
        async with aiopg.connect(PGCONF) as conn:
            cur = await conn.cursor()
            await cur.execute(f"SELECT link FROM links WHERE user_id='{self.user_id}' ORDER BY id DESC")
            result = await cur.fetchall()
            return result