## For beginning:

You should have Firefox, installed not in 'snap'.

Install requirements.txt:

```bash
$ pip install -r tests/requirements.txt
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
