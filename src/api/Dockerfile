FROM python:3.9-alpine
WORKDIR /api
ENV FLASK_APP=./app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc=10.2.1_pre1-r3 musl-dev=1.2.2-r0 linux-headers=5.7.8-r0 postgresql-libs=13.1-r2 postgresql-dev=13.1-r2 postgresql-client=13.1-r2
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD sh ./start.sh db