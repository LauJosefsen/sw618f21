import psycopg2 as psycopg2
from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    connection = psycopg2.connect(
        user="postgres",
        password="password",
        host="db",
        port="5432",
        database="database"
    )
    cursor = connection.cursor()
    query = "SELECT * FROM table"

    cursor.execute(query)
    return {"rows": cursor.fetchall()}
