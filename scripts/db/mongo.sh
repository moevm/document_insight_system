#!/bin/bash

LOADING=false


check_mongo_client()
{
    echo "Checking mongodb-clients is installed"
    if ! dpkg -l mongodb-clients 
    then
        sudo apt update
        sudo apt install -y mongodb-clients
    else
        echo "mongodb-clients already installed"
    fi
}

check_mongo_client

usage()
{
    cat << EOF
    usage: $0 [options] dbname

    OPTIONS:
        -h      Show this help.
        -l      Load instead of export
        -u      Mongo username
        -p      Mongo password
        -H      Mongo host string (ex. localhost:27017)
        -d      Dump path
EOF
}

dumpPath='../dump';
while getopts "hlu:p:d:H:" opt; do
    MAXOPTIND=$OPTIND
    case $opt in
        h)
            usage
            exit
            ;;
        l)
            LOADING=true
            ;;
        u)
            USERNAME="$OPTARG"
            ;;
        p)
            PASSWORD="$OPTARG"
            ;;
        d)
            dumpPath="$OPTARG"
            ;;
        H)
            HOST="$OPTARG"
            ;;
        \?)
            echo "Invalid option $opt"
            exit 1
            ;;
    esac
done

shift $(($MAXOPTIND-1))

if [ -z "$1" ]; then
    echo "Usage: export-mongo [opts] <dbname>"
    exit 1
fi

DB="$1"
path_="${dumpPath}/$DB-dump"
if [ -z "$2" ]; then
    path_="${dumpPath}/$DB-dump"
else
    path_="${dumpPath}/$2"
fi

if [ -z "$HOST" ]; then
    CONN="localhost:27017/$DB"
else
    CONN="$HOST/$DB"
fi

ARGS=""
if [ -n "$USERNAME" ]; then
    ARGS="-u $USERNAME"
fi
if [ -n "$PASSWORD" ]; then
    ARGS="$ARGS -p $PASSWORD"
fi
echo "$ARGS"
echo "*************************** Mongo Export ************************"
echo "**** Host:      $HOST"
echo "**** Database:  $DB"
echo "**** Username:  $USERNAME"
echo "**** Password:  $PASSWORD"
echo "**** Loading:   $LOADING"
echo "**** Dump path: $dumpPath"
echo "*****************************************************************"

if $LOADING ; then
    echo "Loading into $CONN"
    pushd $path_ >/dev/null
    echo $path_
    unzip backup.zip
    for path in *.json; do
        collection=${path%.json}
        echo "Loading into $DB/$collection from $path"
        miout="$(mongoimport  --host $HOST -d $DB -c $collection $path --stopOnError)"
        echo $miout
        if [ $? -gt 0 ]; then
            echo 'Error occured while imorting collection: '${collection}'.'
            exit 1
        fi
        grep --quiet  "E11000" <<< $miout
        if [ $? -eq 0 ]; then
            echo 'Error occured while imorting collection: '${collection}'.'
            exit 1
        fi
    done

    popd >/dev/null
else
    echo "mongo $CONN $ARGS --quiet --eval 'db.getCollectionNames()'"
    DATABASE_COLLECTIONS=$(mongo $CONN $ARGS --quiet --eval 'db.getCollectionNames()' | sed 's/[,"]/ /g;1,1d; $d')

    mkdir -p $(pwd)/${dumpPath}/$DB-dump
    cd $(pwd)/${dumpPath}/$DB-dump

    for collection in $DATABASE_COLLECTIONS; do
        if [[ "${collection}" == "logs" ]]
        then
          echo "Skiping logs"
          continue
        fi
        echo "mongoexport --host $HOST -d $DB -c $collection --out=$collection.json --forceTableScan"
        mongoexport --host $HOST -d $DB -c $collection --out=$collection.json --forceTableScan >/dev/null
    done
    zip -r backup.zip *.json
    rm *.json
    cd -
fi
