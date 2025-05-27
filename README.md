# mse_auto_checking_slides

## Environment
- To `.env` in root:
```
RECAPTCHA_SITE_KEY=
RECAPTCHA_SECRET_KEY=
SECRET_KEY=
ADMIN_PASSWORD=
SIGNUP_PAGE_ENABLED=False

CONSUMER_KEY=
CONSUMER_SECRET=

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

