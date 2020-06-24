from bson.objectid import ObjectId
import re
import aioredis
import pymongo

class UserDB():
    def __init__(self, db, **kwargs):
        self.collection = db['users']
        self.redis_pool = kwargs.get('redis_pool')

    async def list(self):
        cursor = self.collection.find({}, 
            {
                'password': False
            })
        return {'status': 'success', 'data': await cursor.to_list(None)}

    async def item(self, item_id):
        try:
            document = await self.collection.find_one(
                {'_id': ObjectId(item_id)},
                {
                    'password': False
                })
            return {'status': 'success', 'data': document}
        except:
            return {'status': 'error', 'error': 'Failed to get item info'}

    async def insert(self, data):
        data.pop('_id', None)
        try:
            result = await self.collection.insert_one(data)
            if result.inserted_id != None:
                return {"status": "success", 'data': result.inserted_id}
            else:
                return {"status": "error", "error": "Failed to add record"}
        except pymongo.errors.DuplicateKeyError:
            return {"status": "error", "error": "Duplicate key"}

    async def update(self, user_id, data):
        data.pop('_id', None)
        # delete keys with token from redis, find keys by login
        result = await self.item(user_id)
        if result['status'] == 'success':
            user_data = result.get('data')
            if (user_data['permissions'] != data.get('permissions') or 
                user_data['login'] != data.get('login') or
                data.get('password')):
                await self.remove_tokens(user_data.get('login'))
        else:
            return {"status": "error", 'error': result.get('error','user not found')}

        try:
            result = await self.collection.update_one({'_id': ObjectId(user_id)}, {'$set': data})
            if result.matched_count > 0:
                return {"status": "success"}
            else:
                return {"status": "error", "error": "update item failed"}
        except pymongo.errors.DuplicateKeyError:
            return {"status": "error", "error": "Duplicate key"}
    
    async def delete(self, user_id):
        # delete keys with token from redis, find keys by user_id
        result = await self.item(user_id)
        if result['status'] == 'success':
            user_data = result.get('data')
            deleted_login = user_data.get('login')
            if deleted_login:
                await self.remove_tokens(deleted_login)
        else:
            return {"status": "error", 'error': result.get('error','user not found')}

        result = await self.collection.delete_many({'_id': ObjectId(user_id)})
        if result.deleted_count > 0:
            return {"status": "success"}
        else:
            return {"status": "error"}

    async def check_user(self, login, password):
        document = await self.collection.find_one(
            {
                'login': login, 
                'password': password
            },
            {
                '_id': False, 
                'password': False
            })
        return document, str(ObjectId())

    async def remove_tokens(self, login):
        keys = await aioredis.Redis(self.redis_pool).keys('*')
        for key in keys:
            login_from_redis = await aioredis.Redis(self.redis_pool).hget(key, 'login')
            if login_from_redis.decode('UTF-8') == login:
                await aioredis.Redis(self.redis_pool).delete(key)
    

    async def get_settings(self, decoded_token):
        (login, permissions) = await self.get_login(decoded_token)
        document = await self.collection.find_one(
            {'login': login},
            {'settings': True, '_id': False})
        return {'status': 'success', 'data': document}

    async def update_settings(self, decoded_token, data):
        (login, permissions) = await self.get_login(decoded_token)
        if permissions.get('superuser') or \
            permissions.get('devices') in ['read', 'write']:
            devices_output_settings = data.get('devices_output_settings')
            if devices_output_settings:
                result = await self.collection.update_one({'login': login}, 
                        {'$set': {'settings.device_output': devices_output_settings}})
                if result.matched_count > 0:
                    return {"status": "success"}
                else:
                    return {"status": "error", "error": "update settings failed"}

    async def get_login(self, decoded_token):
        user_id = decoded_token.get('user_id', '')
        permissions = decoded_token.get('permissions', {})
        login = await aioredis.Redis(self.redis_pool).hget(user_id, 'login')
        return (login.decode('UTF-8'), permissions)

                    

