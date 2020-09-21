FROM python:3.8

RUN apt-get update && apt-get install -y\
    build-essential \
    git \
    vim \
&& rm -rf /var/lib/apt/list/*

RUN pip install ipython \
    flask \
    datetime \ 
    glob3 


ENTRYPOINT [ "/bin/bash" ]