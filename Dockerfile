FROM python:3.6-slim
WORKDIR /
COPY . /
RUN apt-get update && apt-get -y install libglib2.0-0 libsm6 libxtst6 libxrender-dev; apt-get clean &&  pip3 install --no-cache-dir -r requirements.txt
CMD python ./app.py