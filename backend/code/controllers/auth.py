from aiohttp import web, WSMsgType
import json
import jwt
import aioredis

from models.users import UserDB

class Auth(web.View):

    # authentication by login and password
    async def post(self):
        self.base = UserDB(self.request.app.db)
        results = []
        json_data = await self.request.json()
        login = json_data.get('login')
        password = json_data.get('password')
        exist_user, user_id = await self.base.check_user(login, password)
        if exist_user is None:
            results = {'result': 'error'}
        else:
            # generate JWT with user_id and permissions
            token = jwt.encode({
                'user_id': user_id,
                'permissions': exist_user.get('permissions'),
                }, 
                self.request.app['secret'], 
                algorithm='HS256'
                ).decode("utf-8")

            # keep user_id/token/login/client_ip in redis
            # set that this token valid for 30 days 
            await aioredis.Redis(self.request.app.redis).hset(user_id, 'token', token)
            await aioredis.Redis(self.request.app.redis).hset(user_id, 'login', login)
            await aioredis.Redis(self.request.app.redis).hset(user_id, 'ip', self.request.remote)
            await aioredis.Redis(self.request.app.redis).expire(user_id, timeout=60*60*24*30)

            results = {'result': 'success', 'token': token, 'username': exist_user.get('username')}

        return web.json_response(results)

    async def delete(self):
        # decode user_id from auth token
        token = self.request.headers.get('Authorization')
        if token:
            decoded = jwt.decode(token, self.request.app['secret'], algorithms=['HS256'])
            # remove user_id from redis
            user_id = decoded.get('user_id')
            if user_id:
                await aioredis.Redis(self.request.app.redis).delete(user_id)
        return web.json_response({'result': 'success'})

