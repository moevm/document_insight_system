## For beginning:

You should have Firefox, installed not in 'snap'.

Install requirements.txt:

```bash
$ pip install -r tests/requirements.txt
```


## Test for open single check card:
class SingleCheckTestSelenium(BasicSeleniumTest) with 1 test

Test check: if page with random single check opens (from "/check_list")

## Run run_tests

use login and password from .env

```bash
$ python tests/main.py --host host --login login --password password
```
