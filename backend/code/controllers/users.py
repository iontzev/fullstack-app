from aiohttp import web, WSMsgType
import json
import jwt

from models.users import UserDB
from tools import JSONEncoder
from models.auth import permission_required, auth_required

class Users(web.View):

    # get users list from database
    @permission_required('superuser')
    async def get(self):
        self.base = UserDB(self.request.app.db)
        result = await self.base.list()
        if result.get('status') == 'success':
            data = {'users': result.get('data', [])}
        else:
            data = {'users': []}

        # avoid error with ObjectId->JSON encoding
        str_data = JSONEncoder().encode(data)
        json_data = json.JSONDecoder().decode(str_data)

        return web.json_response(json_data)

class User(web.View):

    # get info about user
    @permission_required('superuser')
    async def get(self):
        self.base = UserDB(self.request.app.db)
        result = await self.base.item(self.request.match_info['user_id'])

        # avoid error with ObjectId->JSON encoding
        str_data = JSONEncoder().encode(result)
        json_data = json.JSONDecoder().decode(str_data)

        return web.json_response(json_data)

    # new user
    @permission_required('superuser')
    async def post(self):
        self.base = UserDB(self.request.app.db)
        json_data = await self.request.json()
        result = await self.base.insert(json_data)

        # avoid error with ObjectId->JSON encoding
        str_data = JSONEncoder().encode(result)
        json_data = json.JSONDecoder().decode(str_data)
 
        return web.json_response(json_data)

    # delete user
    @permission_required('superuser')
    async def delete(self):
        self.base = UserDB(self.request.app.db, redis_pool=self.request.app.redis)
        result = await self.base.delete(self.request.match_info['user_id'])
        return web.json_response(result)

    # update user
    @permission_required('superuser')
    async def put(self):
        self.base = UserDB(self.request.app.db, redis_pool=self.request.app.redis)
        json_data = await self.request.json()
        result = await self.base.update(self.request.match_info['user_id'], json_data)
        return web.json_response(result)

class Settings(web.View):

    # get settings
    @auth_required()
    async def get(self):
        token = self.request.headers.get('Authorization')
        decoded_token = jwt.decode(token, self.request.app['secret'], algorithms=['HS256'])
        self.base = UserDB(self.request.app.db, redis_pool=self.request.app.redis)
        result = await self.base.get_settings(decoded_token)
        return web.json_response(result)

    # update user settings by himself
    @auth_required()
    async def patch(self):
        token = self.request.headers.get('Authorization')
        decoded_token = jwt.decode(token, self.request.app['secret'], algorithms=['HS256'])
        self.base = UserDB(self.request.app.db, redis_pool=self.request.app.redis)
        json_data = await self.request.json()
        result = await self.base.update_settings(decoded_token, json_data)
        return web.json_response(result)
    