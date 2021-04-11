FROM python:3.9
WORKDIR /api
ENV FLASK_APP=./app.py
ENV FLASK_DEBUG=1
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc=4:8.3.0-1 \
  musl-dev=1.1.21-2 \
  libpq-dev=11.11-0+deb10u1 \
  postgresql-client=11+200+deb10u4 \
  && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir pip==21.0.1
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python3", "-m", "flask", "run"]