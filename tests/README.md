
## Docker:

Tests included in docker-compose.yml

You can run tests with dockerfile_selenium independently, using special flag:

```bash
$ docker build -t your_image_name -f Dockerfile_selenium .
$ docker run -e LOGIN=your_login -e PASSWORD=your password --network="host" your_image_name

```

## Test for autorization:
class AuthTestSelenium(BasicSeleniumTest) with 3 tests

Tests check: if page "/login" opens, if it doesn't take wrong login/password and takes correct.

## Test for open page /check_list:
class StatisticTestSelenium(BasicSeleniumTest) with 1 test

Test check: if page "/check_list" opens


## Run run_tests

use login and password from .env

```bash
$ python tests/main.py --host host --login login --password password
```
