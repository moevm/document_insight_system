
## For local tests:

```bash
$ pip install -r tests/requirements.txt
```

### Run tests:

use login and password from .env

```bash
$ python3 tests/main.py --host host --login login --password password --pres your press
```

## Docker:

You can run tests with dockerfile_selenium independently, using special flag:

```bash
$ docker build -t your_image_name -f Dockerfile_selenium .
$ docker run -e LOGIN=your_login -e PASSWORD=your password --network="host" your_image_name

```
## List of tests:

### Test for autorization:

class AuthTestSelenium(BasicSeleniumTest) with 3 tests
Tests check: if page "/login" opens, if it doesn't take wrong login/password and takes correct.

### Test for open page /check_list:

class StatisticTestSelenium(BasicSeleniumTest) with 1 test
Test check: if page "/check_list" opens


### Test for loading presentation:

class PresLoadTestSelenium(BasicSeleniumTest) with 1 test
Test check: if the presentation loads correctly
use path to "example_of_pres.pptx" from "/tests" (default) or your own example

### Test for open single check card:

class SingleCheckTestSelenium(BasicSeleniumTest) with 1 test
Test check: if page with random single check opens (from "/check_list")

### Test for open page /version:

class VersionTestSelenium(BasicSeleniumTest) with 1 test
Test check: if page "/version" opens and contains info from "VERSION.json"
