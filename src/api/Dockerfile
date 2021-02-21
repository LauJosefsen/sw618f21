FROM python:3.9-slim
WORKDIR /api
ENV FLASK_APP=./app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt update
RUN apt install -y gcc musl-dev libpq-dev postgresql-client
#RUN apk add --no-cache
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD sh ./start.sh db