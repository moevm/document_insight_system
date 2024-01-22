## For beginning:

Install:
pip install selenium
(selenium==4.16.0 (in this version you don't need to download geckodriver))

pip install webdriver-manager (to avoid problem with binary. And you should have Firefox installed not in 'snap')
webdriver-manager==4.0.1

## Test for autorization:
class AuthTestSelenium(BasicSeleniumTest) with 3 tests

Tests check: if page "/login" opens, if it doesn't take wrong login/password and takes correct.

## Run run_tests

use login and password from .env

```bash
$ python tests/main.py --host host --login login --password password
```
