import os

import csv

from model.ais_data_entry import AisDataEntry
from service.ais_data_service import AisDataService


class Importer:
    def __init__(self):
        self.ais_data_service = AisDataService()

    def import_files(self, path):
        print("Im alive")
        for entry in os.scandir(path):

            if not entry.is_dir() and ".csv" in entry.name:
                self.ais_data_service.import_file(entry.path)



print("REEEEEE")
Importer().import_files("import")
