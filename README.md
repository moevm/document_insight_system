# mse_auto_checking_slides

## Environment
- To `.env` in root:
```
RECAPTCHA_SITE_KEY=...
RECAPTCHA_SECRET_KEY=...
SECRET_KEY=...
ADMIN_PASSWORD=...
SIGNUP_PAGE_ENABLED=...

CONSUMER_KEY=...
CONSUMER_SECRET=...
```

## Run  
```
docker-compose up
```

## Deploy
```
./scripts/restart.sh <apache_conf>
```
