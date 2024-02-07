## For beginning:

You should have Firefox, installed not in 'snap'.

Install requirements.txt:

```bash
$ pip install -r tests/requirements.txt
```


## Test for open page /version:
class VersionTestSelenium(BasicSeleniumTest) with 1 test

Test check: if page "/version" opens and contains info from "VERSION.json"

## Run run_tests

use login and password from .env

```bash
$ python tests/main.py --host host --login login --password password
```
