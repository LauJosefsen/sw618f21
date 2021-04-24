import configparser
import multiprocessing

from psycopg2.pool import ThreadedConnectionPool
import psycopg2


class SqlConnector:

    # Database connection:
    config = configparser.ConfigParser()
    config.read("sql.ini")

    __database = config["sql"]["database"]
    __user = config["sql"]["user"]
    __pasword = config["sql"]["password"]
    __host = config["sql"]["host"]
    __port = config["sql"]["port"]

    # used for psycopg2
    dsn = f"dbname={__database} user={__user} password={__pasword} host={__host} port={__port}"
    # used for d6tstack utilities when importing csv files.
    cfg_uri_psql = (
        f"postgresql+psycopg2://{__user}:{__pasword}@{__host}:{__port}/{__database}"
    )

    tcp = ThreadedConnectionPool(4, max(4, multiprocessing.cpu_count()), dsn=dsn)

    def get_db_connection(self):
        return psycopg2.connect(dsn=self.dsn)

    @staticmethod
    def get_db_connection_from_thread_pool():
        # todo: Might be interesting to keep a global thread pool, and just "lease" connections when requested.
        pass
