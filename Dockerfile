FROM ubuntu:18.04
ENV LANG en_US.UTF-8

ADD . /usr/src/project
WORKDIR /usr/src/project

RUN apt-get update
RUN apt install -y python3-pip python3.8-dev


RUN python3.8 -m pip install Flask==1.1.2 requests==2.24.0 python-pptx==0.6.18 odfpy==1.4.1 pymongo==3.11.1 flask-login==0.5.0 numpy==1.19.4 gensim==3.8.3 pymorphy2==0.9.1 nltk==3.5
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/project"
EXPOSE 8080

CMD ["python3.8", "./app/server.py", "--host", "0.0.0.0"]
