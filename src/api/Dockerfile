FROM python:3.9-slim
WORKDIR /api
ENV FLASK_APP=./app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get update; apt-get install -y --no-install-recommends gcc musl-dev libpq-dev postgresql-client; rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ['sh ','./start.sh']