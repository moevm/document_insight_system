# mse_auto_checking_slides

## Environment
- To `.env` in root:
```
RECAPTCHA_SITE_KEY=6LcxHtkaAAAAAEY7QuH8VfqdIKUSrc34MhRPtjn6
RECAPTCHA_SECRET_KEY=6LcxHtkaAAAAAIBLtJPX1R8krHYmXfkgedskOnXH
SECRET_KEY=21oiw38heheg8162JE91Je7f
ADMIN_PASSWORD=PASSWORD
SIGNUP_PAGE_ENABLED=False

CONSUMER_KEY=consumertestkeyconsumer
CONSUMER_SECRET=consumersecrettestconsumer

WEB_PORT=8080

REDIS_URL=redis://redis:6379/0
CELERY_QUERIES=check-solution,passback-grade

FLOWER_SECRET_KEY=SECRET_KEY
FLOWER_PORT=5555
FLOWER_AUTH=admin:password
FLOWER_PREFIX=/monitoring

MONGODB_CACHE_SIZE=1
CONTAINER_CPU=0


ACCESS_TOKEN=1234567890

DB_PORT_27017_TCP_ADDR=db

```

## Run  
```
docker-compose build
docker-compose up
```

## Deploy
```
./scripts/restart.sh <apache_conf>
```
