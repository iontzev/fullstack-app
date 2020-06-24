from bson.objectid import ObjectId
import re

class DeviceDB():
    def __init__(self, db, **kwargs):
        self.collection = db['devices']

    async def item(self, name):
        document = await self.collection.find_one({'name': name})
        return document

    async def insert(self, data):
        result = await self.collection.insert_one(data)
        if result.inserted_id != None:
            data = {"result": "success", "message": "Record successfully added"}
        else:
            data = {"result": "error", "message": "Failed to add record"}
        return data
    
    # async def update(self, item_id, data):
    #     result = await self.collection.update_one({'_id': ObjectId(item_id)}, {'$set': data})
    #     if result.matched_count > 0:
    #         data = {"result": "success", "message": "Record successfully updated"}
    #     else:
    #         data = {"result": "error", "message": "Failed to update record"}
    #     return data
    
    # async def delete(self, item_id=None):
    #     if item_id is None:
    #         result = await self.collection.delete_many({})
    #         return {"result": "success", "message": "All records successfully deleted"}
    #     result = await self.collection.delete_many({'_id': ObjectId(item_id)})
    #     if result.deleted_count > 0:
    #         data = {"result": "success", "message": "Record successfully deleted"}
    #     else:
    #         data = {"result": "error", "message": "Failed to delete record"}
    #     return data
    

