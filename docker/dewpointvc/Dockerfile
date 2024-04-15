FROM python:3.10-alpine

RUN mkdir /dewpointvc
WORKDIR /dewpointvc

COPY src/requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt


COPY src/dewpointvc dewpointvc
COPY src/setup.py .


RUN python3 setup.py install
