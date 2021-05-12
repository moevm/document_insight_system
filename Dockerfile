FROM ubuntu:18.04
ENV LANG en_US.UTF-8

ADD . /usr/src/project
WORKDIR /usr/src/project

RUN apt-get update
RUN apt-get -y install curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_10.x  | bash -
RUN apt-get -y install nodejs

COPY package*.json .
RUN npm install
RUN npm install webpack
RUN apt install -y python3-pip python3.8-dev

COPY webpack.config.js .
COPY dependencies.txt .
#RUN python3.8 -m pip install Flask==1.1.2 requests==2.24.0 python-pptx==0.6.18 odfpy==1.4.1 pymongo==3.11.1 flask-login==0.5.0 numpy==1.19.4 gensim==3.8.3 pymorphy2==0.9.1 nltk==3.5
RUN  python3.8 -m pip install -r dependencies.txt
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/project"
EXPOSE 8080

COPY act.sh .
RUN ./act.sh -b 
CMD ["python3.8", "./app/server.py", "--host", "0.0.0.0"]
