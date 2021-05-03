import configparser
import multiprocessing

import numpy as np
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
from psycopg2.pool import ThreadedConnectionPool

register_adapter(np.int64, AsIs)


class SqlConnector:

    # Database connection:
    def __init__(self):
        try:
            config = configparser.ConfigParser()
            config.read("sql.ini")

            database = config["sql"]["database"]
            user = config["sql"]["user"]
            password = config["sql"]["password"]
            host = config["sql"]["host"]
            port = config["sql"]["port"]
        except KeyError:
            database = ""
            user = ""
            password = ""
            host = ""
            port = ""

        # used for psycopg2
        self.dsn = (
            f"dbname={database} user={user} password={password} host={host} port={port}"
        )
        # used for d6tstack utilities when importing csv files.
        self.cfg_uri_psql = (
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        )

    def get_db_connection(self):
        return psycopg2.connect(dsn=self.dsn)

    def get_threading_pool(self):
        return ThreadedConnectionPool(1, multiprocessing.cpu_count(), dsn=self.dsn)
