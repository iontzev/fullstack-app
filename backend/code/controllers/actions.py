from aiohttp import web, WSMsgType
import json

from models.actions import ActionsModel
from models.auth import permission_required

class ImportJson(web.View):
    # import devices from JSON file to database
    @permission_required('devices', ['read', 'write'])
    async def post(self):
        json_data = await self.request.json()
        actions = ActionsModel(self.request.app)
        results = await actions.import_json(json_data)

        return web.json_response(results)

    async def get(self):
        return web.json_response('{"test": "test"}')

