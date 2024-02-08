## For beginning:

You should have Firefox, installed not in 'snap'.
There should be setting for "DEFAULT_PRES_TYPE_INFO" in pre_luncher.py

Install requirements.txt:

```bash
$ pip install -r tests/requirements.txt
```


## Test for loading presentation:
class PresLoadTestSelenium(BasicSeleniumTest) with 1 test

Test check: if the presentation loads correctly

## Run run_tests

use login and password from .env
use path to "example_of_pres.pptx" from "/tests" or your own example

```bash
$ python tests/main.py --host host --login login --password password --pres your press
```
