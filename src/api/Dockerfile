FROM python:3.9-slim
WORKDIR /api
ENV FLASK_APP=./app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get update; apt-get install -y --no-install-recommends gcc=4:10.2.0-1ubuntu1 musl-dev=1.2.1-1 libpq-dev=9.5.24-0ubuntu0.16.04.1 postgresql-client=9.5+173ubuntu0.3; rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ['sh','./start.sh']