FROM nickgryg/alpine-pandas:latest
WORKDIR /dash
ENV FLASK_APP=./app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev g++ \
    libffi-dev openssl-dev \
    libxml2 libxml2-dev \
    libxslt libxslt-dev \
    libjpeg-turbo-dev zlib-dev
RUN pip install --upgrade cython
RUN pip install --upgrade pip
ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./ ./

EXPOSE 4000

CMD ["python", "./app.py"]