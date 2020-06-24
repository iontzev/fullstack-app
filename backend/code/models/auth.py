import jwt
from aiohttp import web
import aioredis

def permission_required(section='superuser', required_permissions=[True]):
    """ Check permissions and allow only good users """
    def wrap(func):
        async def wrapped(self, *args, **kwargs):
            if 'Authorization' in self.request.headers:
                try:
                    token = self.request.headers.get('Authorization')
                    decoded = jwt.decode(token, self.request.app['secret'], algorithms=['HS256'])
                    permissions = decoded.get('permissions', {})
                    user_id = decoded.get('user_id', '')
                except:
                    # token decode failed
                    raise web.HTTPUnauthorized(reason='Invalid authorization header')
            else:
                raise web.HTTPUnauthorized(reason='Access without authorization is not allowed')

            # check for token exist in database
            required_token = await aioredis.Redis(self.request.app.redis).hget(user_id, 'token')
            required_token = required_token.decode('UTF-8') if required_token else ''
            if token != required_token:
                # token changed on client side
                raise web.HTTPUnauthorized(reason='Invalid authorization token')

            # check permissions required for this request
            if permissions.get('superuser') != True:
                existed_permission = permissions.get(section, 'none')
                if existed_permission not in required_permissions:
                    raise web.HTTPForbidden(reason='Access forbidden')

            return await func(self, *args, **kwargs)
        return wrapped
    return wrap

def auth_required():
    """ Allow only authenticated users """
    def wrap(func):
        async def wrapped(self, *args, **kwargs):
            if 'Authorization' in self.request.headers:
                try:
                    token = self.request.headers.get('Authorization')
                    decoded = jwt.decode(token, self.request.app['secret'], algorithms=['HS256'])
                    permissions = decoded.get('permissions', {})
                    user_id = decoded.get('user_id', '')
                except:
                    # token decode failed
                    raise web.HTTPUnauthorized(reason='Invalid authorization header')
            else:
                raise web.HTTPUnauthorized(reason='Access without authorization is not allowed')

            # check for token exist in database
            required_token = await aioredis.Redis(self.request.app.redis).hget(user_id, 'token')
            required_token = required_token.decode('UTF-8') if required_token else ''
            if token != required_token:
                # token changed on client side
                raise web.HTTPUnauthorized(reason='Invalid authorization token')

            return await func(self, *args, **kwargs)
        return wrapped
    return wrap
