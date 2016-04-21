FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y node-less yui-compressor gettext
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
