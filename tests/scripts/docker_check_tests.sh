# !/bin/bash

service="selenium-tests"
container_id=$(docker-compose -f docker-compose-tests.yml ps -q $service)


while true; do

    if docker ps -a -q | grep -q "^${container_id}$"; then
        if docker inspect --format='{{.State.Running}}' "$container_id" | grep -q "false"; then
            echo "tests are finished"
            EXIT_CODE=$(docker inspect "$container_id" --format='{{.State.ExitCode}}')
            docker-compose -f docker-compose-tests.yml logs selenium-tests
            if [ "$EXIT_CODE" -eq 0 ]; then
                echo "tests finished with code $EXIT_CODE (OK)"
                exit 0
            else
                echo "tests are failed, code $EXIT_CODE"
                exit 1
            fi
        else
            echo "tests in progress"
            sleep 30
        fi
    else
        echo "Контейнер сервиса $service не найден."
        exit 1
    fi

done


# in case of return logs:
# while true; do
#     test_end=$(docker-compose -f docker-compose-tests.yml logs selenium-tests | grep -q "Ran"; echo $?)

#     if [ "$test_end" -eq 0 ]; then
#         echo "tests are finished"
#         exit 0
#     else
#         sleep 60
#         echo "in progress"
#     fi
# done
