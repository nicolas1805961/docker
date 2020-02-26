FROM python:3.6
WORKDIR /
COPY . /
RUN pip3 install -r requirements.txt
CMD /usr/local/bin/python ./app.py