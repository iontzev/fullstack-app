db.createUser(
    {
        user: "devman",
        pwd: "devman",
        roles :[ { role: "readWrite", db: "devman"}]
    }
)

db.users.insert(
    {
        username: 'Administrator',
        login: "admin",
        password: "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
        permissions: {
            superuser: true
        }
    }
)
db.users.insert(
        {
        username: 'User',
        login: "user",
        password: "04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb",
        permissions: {
            superuser: false,
            devices: 'write',
            users: 'read',
            reports: 'read'
        }
    }
)

db.users.createIndex({login:1}, {unique:true})
db.users.createIndex({username:1}, {unique:true})
db.devices.createIndex({name:1}, {unique:true})
db.devices.createIndex({"management.address":1}, {unique:true})
