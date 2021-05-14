#!/bin/bash

BAD='\u001b[1m\u001b[31m'
GOOD='\u001b[1m\u001b[32m'
OK='\u001b[0m'



help()
{
  echo "Run \"./act.sh [keys]\" with following keys:"
  echo "\"-h\" to see this message again"
  echo "\"-i\" to check and/or install dependencies of the app"
  echo "\"-b\" to build the app and prepare to launch"
  echo "\"-d\" to launch in development mode"
  echo "\"-p\" to launch in production mode"
  echo "... or their combinations! (e.g. \"./act.sh -i -b -p\" for quick deploy)"
}

install()
{
  {
    python3 -m pip --version > /dev/null && echo -e "${GOOD}Python and pip are proved to be installed!${OK}"
  } || {
    echo -e "${BAD}Please, install python3 and pip to proceed!${OK}"
    exit
  }

  xargs -I %s python3 -m pip install %s < ./dependencies

  {
    npm -v > /dev/null && echo -e "${GOOD}Node.js and npm are proved to be installed!${OK}"
  } || {
    echo -e "${BAD}Please, install Node.js and npm to proceed!${OK}"
    exit
  }

  npm install -production=false
}



if [ $# -eq 0 ]
  then
    help
    exit
fi

while getopts hibdp flag
do
  case "${flag}" in
    h) help;;
    i) install;;
    b) npm run build;;
    d) ./venv/bin/python3 -m app.server -d;;
    p) ./venv/bin/python3 -m app.server -p;;
    *) help;;
  esac
done
