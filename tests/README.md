## For beginning:

Install:
pip install selenium
(selenium==4.16.0 (in this version you don't need to download geckodriver))

pip install webdriver-manager (to avoid problem with binary. And you should have Firefox installed not in 'snap')
webdriver-manager==4.0.1

## Test for open page debug:
class VersionTestSelenium(BasicSeleniumTest) with 1 test

Test check: if page "/version" opens and contains info from "VERSION.json"

## Run run_tests

use login and password from .env

```bash
$ python tests/main.py --host host --login login --password password
```
