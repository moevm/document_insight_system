# !/bin/bash

while true; do
    test_end=$(docker-compose -f docker-compose-tests.yml logs selenium-tests | grep -q "Ran"; echo $?)

    if [ "$test_end" -eq 0 ]; then
        echo "test finished"
        exit 0
    else
        sleep 60
    fi
done

