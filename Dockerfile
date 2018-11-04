FROM ubuntu:16.04

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y locales locales-all
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.4 python3.5 python3.6 python3.7 python-pip
RUN pip install pipenv
