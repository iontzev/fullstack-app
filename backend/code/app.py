import asyncio
from aiohttp import web

import aioreloader
import logging
import jwt

from motor import motor_asyncio as ma
import aioredis

from settings import *
from routes import routes

async def make_redis_pool():
    return await aioredis.create_pool((REDIS_HOST, REDIS_PORT))



if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    redis_pool = loop.run_until_complete(make_redis_pool())
    
    app = web.Application()

    app.logger = logging.getLogger('webapp')
    app.logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('webapp.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    app.logger.addHandler(fh)
    app.logger.info('START LOGGING')
    
    aioreloader.start()
    
    app.redis = redis_pool
    app['api_history'] = {}
    app['secret'] = SECRET_FOR_GENERATE_TOKEN
    
    app.client = ma.AsyncIOMotorClient(MONGO_HOST)
    app.db = app.client[MONGO_DATABASE]
    
    # make routes
    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])

    web.run_app(app, port=80)

