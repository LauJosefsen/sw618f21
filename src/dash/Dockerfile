FROM python:3.9-slim
WORKDIR /dash
ENV FLASK_APP=./app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip3 install pip==20.3.4
EXPOSE 4000
CMD ["python", "-u", "./app.py"]