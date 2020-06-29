from bson.objectid import ObjectId
import json
import re

from models.devices import DeviceDB

class ActionsModel():
    def __init__(self, app, **kwargs):
        self.app = app
        self.base = DeviceDB(self.app.db)

    async def import_json(self, json_data):
        results = []
        # check for settings in json data
        settings = json_data.get('settings', {})
        replace_items = settings.get('replace_item_with_same_name', False)
        delete_all_items = settings.get('delete_all_items_before_upload', False)
        
        if delete_all_items:
            result = await self.base.delete_all()
            if result.get('status') == 'success':
                results.append(f'Deleted all ({result.get("data")}) records')
        
        default_device = json_data.get('default_device', {})
        devices = json_data.get('devices', [])
        for item in devices:
            device = self.rec_merge(item, default_device)
            name = device.get('name')
            if name is None:
                results.append('Device name is missing')
            else:
                result = await self.base.item_by_name(name)
                exist_item = None
                if result.get('status') == 'success':
                    exist_item = result.get('data')
                if exist_item is None:
                    result = await self.base.insert(device)
                    if result.get('status') == 'success':
                        results.append(f'Added device {name}')
                    else:
                        results.append(f'Can\'t add device {name} - {result.get("error")}')

                else:
                    if replace_items:
                        result = await self.base.update(exist_item.get('_id'), device)
                        if result.get('status') == 'success':
                            results.append('Updated device ' + name)
                        else:
                            results.append(f'Can\'t update device {exist_item.get("name")} - {result.get("error")}')
                    else:
                        results.append(f'Device with name {name} already exist')
        return results

    async def export_json(self, settings):
        json_data = {
            'settings': {
                'replace_item_with_same_name': settings.get('replace_item_with_same_name', True),
                'delete_all_items_before_upload': settings.get('delete_all_items_before_upload', False)
            },
            'default_device': {
                'vendor': '',
                'type': 'router',
                'management': {
                'protocol': 'ssh',
                'cli_username': '',
                }
            }
        }
        flag_export_passwords = settings.get('flag_export_passwords', False)
        if flag_export_passwords:
            json_data['default_device']['management']['snmp_read_community'] = ''
            json_data['default_device']['management']['cli_password'] = ''
            json_data['default_device']['management']['cli_enable_password'] = ''

        result = await self.base.list_for_import(flag_export_passwords)
        if result.get('status') == 'success':
            json_data['devices'] = result.get('data', [])
        return json_data


    def rec_merge(self, d1, d2):
        '''return new merged dict of dicts'''
        if isinstance(d1, dict):
            for k, v in d1.items():
                if k in d2:
                    d2[k] = self.rec_merge(v, d2[k])
            d3 = d1.copy()
            d3.update(d2)
            return d3
        else:
            return d1
