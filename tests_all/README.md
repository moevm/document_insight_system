
## For local tests:

```bash
$ pip install -r tests/requirements.txt
```

### Run tests:

use login and password from .env
You can run tests with your own data:

```bash

$ python3 tests/main.py --host host --login login --password password --pres your press --report your report --report_doc your report doc
```

or use default setting:

```bash
$ python3 tests/main.py --login login --password password
```

## Docker:

### Dockerfile
You can run tests with dockerfile_selenium independently, using special flag:

```bash
$ docker build -t your_image_name -f Dockerfile_selenium .
$ docker run -e LOGIN=your_login -e PASSWORD=your password --network="host" your_image_name

```

### Docker-compose
You can run docker-compose-selenium with docker-compose:

```bash
$ docker-compose -f docker-compose.yml -f docker-compose-selenium.yml build
$ docker-compose -f docker-compose.yml -f docker-compose-selenium.yml up

```

## List of tests:

### Test for autorization:

class AuthTestSelenium(BasicSeleniumTest) with 3 tests
Tests check: if page "/login" opens, if it doesn't take wrong login/password and takes correct.

### Test for open page /check_list:

class StatisticTestSelenium(BasicSeleniumTest) with 1 test
Test check: if page "/check_list" opens


### Test for open single check card:

class SingleCheckTestSelenium(BasicSeleniumTest) with 1 test
Test check: if page with random single check opens (from "/check_list")

### Test for open page /version:

class VersionTestSelenium(BasicSeleniumTest) with 1 test
Test check: if page "/version" opens and contains info from "VERSION.json"

### Test for loading report and pres:

class FileLoadTestSelenium(BasicSeleniumTest) with 3 tests
Test check: if reports wit different extensions loads correctly
use default documents from "/tests" or your own example


