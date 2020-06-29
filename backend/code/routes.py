from controllers.auth import Auth
from controllers.actions import ImportJson, ExportJson
from controllers.users import Users, User, Settings
from controllers.devices import Devices, Device

routes = [
    ('*', '/auth', Auth, 'login_logout'),

    ('GET', '/users', Users, 'users_get'),
    ('*', '/user/{user_id}', User, 'user_get_put_delete'),
    ('POST', '/user/', User, 'user_post'),
    ('*', '/user_settings', Settings, 'settings_get_patch'),

    ('GET', '/devices', Devices, 'device_get'),
    ('*', '/device/{device_id}', Device, 'device_get_put_patch_delete'),
    ('POST', '/device/', Device, 'device_post'),

    ('POST', '/import_json', ImportJson, 'import_json_post'),
    ('POST', '/export_json', ExportJson, 'export_json_post'),
]