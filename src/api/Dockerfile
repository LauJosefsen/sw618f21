FROM python:3.9-buster
WORKDIR /api
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  musl-dev \
  libpq-dev \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir pip==21.0.1
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python3", "-m", "flask", "run"]