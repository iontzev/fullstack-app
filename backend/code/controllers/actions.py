from aiohttp import web, WSMsgType
import json

from models.actions import DeviceDB

class ImportJson(web.View):
    # import from JSON file to database
    async def post(self):
        self.base = DeviceDB(self.request.app.db)
        results = []
        json_data = await self.request.json()

        # check for settings in json data
        settings = json_data.get('settings', {})
        replace_items = settings.get('replace_item_with_same_name', False)
        delete_all_items = settings.get('delete_all_items_before_upload', False)

        if delete_all_items:
            result = await self.base.delete()
            results.append(result['message'])
        
        devices = json_data.get('devices', [])
        for item in json_data.get('devices'):
            name = item.get('name')
            if name is None:
                results.append('Device name is missing')
            else:
                exist_item = await self.base.item(name)
                if exist_item is None:
                    result = await self.base.insert(item)
                    results.append('Added device ' + name)
                else:
                    if replace_items:
                        result = await self.base.update(exist_item['_id'], item)
                        results.append('Updated device ' + name)
                    else:
                        results.append('Device with name ' + name + ' already exist')
            
        return web.json_response(results)

    async def get(self):
        return web.json_response('{"test": "test"}')

