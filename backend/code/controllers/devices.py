from aiohttp import web, WSMsgType
import json

from models.devices import DeviceDB
from tools import JSONEncoder
from models.auth import permission_required

class Devices(web.View):

    # get devices list from database
    @permission_required('devices', ['read', 'write'])
    async def get(self):
        self.base = DeviceDB(self.request.app.db)
        result = await self.base.list()
        if result.get('status') == 'success':
            data = {'devices': result.get('data', [])}
        else:
            data = {'devices': []}
        
        # avoid error with ObjectId->JSON encoding
        str_data = JSONEncoder().encode(data)
        json_data = json.JSONDecoder().decode(str_data)

        self.request.app.logger.info(json_data)

        return web.json_response(json_data)

class Device(web.View):

    # get device data from database
    @permission_required('devices', ['read', 'write'])
    async def get(self):
        self.base = DeviceDB(self.request.app.db)
        result = await self.base.item(self.request.match_info['device_id'])
        
        # avoid error with ObjectId->JSON encoding
        str_data = JSONEncoder().encode(result)
        json_data = json.JSONDecoder().decode(str_data)

        return web.json_response(json_data)

    @permission_required('devices', ['write'])
    async def post(self):
        self.base = DeviceDB(self.request.app.db)
        json_data = await self.request.json()

        result = await self.base.insert(json_data)

        # avoid error with ObjectId->JSON encoding
        str_data = JSONEncoder().encode(result)
        json_data = json.JSONDecoder().decode(str_data)
        
        return web.json_response(json_data)

    @permission_required('devices', ['write'])
    async def delete(self):
        self.base = DeviceDB(self.request.app.db)
        
        result = await self.base.delete(self.request.match_info['device_id'])
        return web.json_response(result)

    
    @permission_required('devices', ['write'])
    async def put(self):
        self.base = DeviceDB(self.request.app.db)
        json_data = await self.request.json()
        result = await self.base.update(self.request.match_info['device_id'], json_data)
        return web.json_response(result)

    

