#import base image
FROM python:3.6-slim
#specify current wordir in container
WORKDIR /
#copy everything from host context (except filenames in .dockerignore)
COPY . /
#run command to install packages (use && not to add layers)
RUN apt-get update && apt-get -y install libglib2.0-0 libsm6 libxtst6 libxrender-dev; apt-get clean &&  pip3 install --no-cache-dir -r requirements.txt
#launch server thanks to the app.py file
CMD python ./app.py