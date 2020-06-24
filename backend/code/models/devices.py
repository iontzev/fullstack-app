from bson.objectid import ObjectId
import re
import pymongo

import rncryptor

from settings import SECRET_FOR_CRYPT_PASSWORDS

class DeviceDB():
    def __init__(self, db, **kwargs):
        self.collection = db['devices']

    async def list(self):
        cursor = self.collection.find({},{
            'management.snmp_read_community': False,
            'management.cli_password': False,
            'management.cli_enable_password': False,
        })
        return {'status': 'success', 'data': await cursor.to_list(None)}

    async def item(self, item_id):
        try:
            document = await self.collection.find_one(
                {'_id': ObjectId(item_id)},
                {
                    'management.snmp_read_community': False,
                    'management.cli_password': False,
                    'management.cli_enable_password': False,
                })
            return {'status': 'success', 'data': document}
        except:
            return {'status': 'error', 'error': 'Failed to get item info'}

    async def insert(self, data):
        data.pop('_id', None)
        data = self.encrypt_passwords(data)
        try:
            result = await self.collection.insert_one(data)
            if result.inserted_id != None:
                return {"status": "success", 'data': result.inserted_id}
            else:
                return {"status": "error", "error": "Failed to add record"}
        except pymongo.errors.DuplicateKeyError:
            return {"status": "error", "error": "Duplicate key"}
    
    async def update(self, item_id, data):
        data.pop('_id', None)
        data = self.encrypt_passwords(data)
        try:
            result = await self.collection.update_one({'_id': ObjectId(item_id)}, {'$set': data})
            if result.matched_count > 0:
                return {"status": "success"}
            else:
                return {"status": "error", "error": "update item failed"}
        except pymongo.errors.DuplicateKeyError:
            return {"status": "error", "error": "Duplicate key"}
    
    async def delete(self, item_id):
        result = await self.collection.delete_many({'_id': ObjectId(item_id)})
        if result.deleted_count > 0:
            return {"status": "success"}
        else:
            return {"status": "error"}

    def encrypt_passwords(self, data):
        cryptor = rncryptor.RNCryptor()
        if 'snmp_read_community' in data['management'] and data['management']['snmp_read_community']:
            crypted_text = cryptor.encrypt(data['management']['snmp_read_community'], SECRET_FOR_CRYPT_PASSWORDS)
            data['management']['snmp_read_community'] = crypted_text
        if 'cli_password' in data['management'] and data['management']['cli_password']:
            crypted_text = cryptor.encrypt(data['management']['cli_password'], SECRET_FOR_CRYPT_PASSWORDS)
            data['management']['cli_password'] = crypted_text
        if 'cli_enable_password' in data['management'] and data['management']['cli_enable_password']:
            crypted_text = cryptor.encrypt(data['management']['cli_enable_password'], SECRET_FOR_CRYPT_PASSWORDS)
            data['management']['cli_enable_password'] = crypted_text
        return data
