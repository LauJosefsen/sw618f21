import multiprocessing
import os

from joblib import Parallel, delayed

from ais_app.repository.ais_data_repository import AisDataRepository


class ImportAisService:
    __ais_data_repository = AisDataRepository()

    def import_ais_data(self):
        print("Importing ais data..")
        path_list = [
            entry.path
            for entry in os.scandir("./import")
            if not entry.is_dir() and ".csv" in entry.name
        ]

        Parallel(n_jobs=multiprocessing.cpu_count())(
            delayed(self.__ais_data_repository.import_csv_file)(path)
            for path in path_list
        )
