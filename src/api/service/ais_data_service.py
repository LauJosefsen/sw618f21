import psycopg2


class AisDataService:
    def __init__(self):
        self.connection = psycopg2.connect(
            user="postgres",
            password="password",
            host="db",
            port="5432",
            database="ais",
        )

    def fetch_all(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM ais.data"

        cursor.execute(query)
        return [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

    @staticmethod
    def __build_dict(cursor, row):
        x = {}
        for key, col in enumerate(cursor.description):
            x[col[0]] = row[key]
        return x
