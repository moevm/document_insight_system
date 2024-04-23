# !/bin/bash

service="selenium-tests"
container_id=$(docker-compose -f docker-compose.yml -f docker-compose-selenium.yml ps -q $service)

if [ -z "$container_id" ]; then
    echo "Контейнер сервиса $service не найден."
    exit 1
fi

while [ "$(docker inspect --format='{{.State.Running}}' "$container_id")" == "true" ]; do
    echo "tests in progress"
    sleep 30
done

echo "tests are finished"

EXIT_CODE=$(docker inspect "$container_id" --format='{{.State.ExitCode}}')
echo "tests logs:"
docker-compose -f docker-compose.yml -f docker-compose-selenium.yml logs selenium-tests
echo "web logs:"
docker-compose logs web
echo "worker logs:"
docker-compose logs worker

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "tests finished with code $EXIT_CODE (OK)"
    exit 0
else
    echo "tests are failed, code $EXIT_CODE"
    exit 1
fi
