FROM postgis/postgis:13-3.1-alpine
WORKDIR /src/db
ENV POSTGRES_PASSWORD=password
COPY init.sql /docker-entrypoint-initdb.d/