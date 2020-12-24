FROM python:3.8

RUN mkdir -p /usr/src/project
WORKDIR /usr/src/project
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/project"

COPY . /usr/src/project
RUN pip install -r dependencies

EXPOSE 8080

CMD ["python3", "./app/server.py"]