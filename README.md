# Fullstack web-app for network equipment management

Structure:
- backend: Rest API server on Python (aiohtpp)
- database: MongoDB
- cache: Redis
- frontend: SPA (Vue.js)

Quick start:
- create project directory `mkdir ~/equipment`
- download code `git clone https://github.com/iontzev/fullstack-app.git ~/equipment`
- start environment in docker `cd ~/equipment && docker-compose up`
- open in browser http://localhost:5000