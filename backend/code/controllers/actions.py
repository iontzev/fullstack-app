from aiohttp import web, WSMsgType
import json

from models.actions import ActionsModel
from models.auth import permission_required

class ImportJson(web.View):
    # import devices from JSON file to database
    @permission_required('devices', ['write'])
    async def post(self):
        json_data = await self.request.json()
        actions = ActionsModel(self.request.app)
        results = await actions.import_json(json_data)

        return web.json_response(results)

class ExportJson(web.View):
    # export devices from database file to JSON
    @permission_required('devices', ['write'])
    async def post(self):
        settings = await self.request.json()
        actions = ActionsModel(self.request.app)
        results = await actions.export_json(settings)

        return web.json_response(results)
