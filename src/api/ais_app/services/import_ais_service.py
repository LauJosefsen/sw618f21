import multiprocessing
import os
from datetime import datetime
import d6tstack.utils
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from ais_app.repository.sql_connector import SqlConnector


class ImportAisService:
    def import_ais_data(self):
        print("Importing ais data..")
        path_list = [
            entry.path
            for entry in os.scandir("./import")
            if not entry.is_dir() and ".csv" in entry.name
        ]

        Parallel(n_jobs=multiprocessing.cpu_count())(
            delayed(self.import_csv_file)(path) for path in path_list
        )

    def import_csv_file(self, csv_fname):
        def apply_string_format(str_input: str):
            if str_input == "nan":
                return None
            str_input = str_input.replace("\\", "\\\\")
            str_input = str_input.replace(",", r"\,")
            return str_input

        def apply_datetime_if_not_none(str_in):
            if str_in == "nan":
                return None
            return datetime.strptime(str_in, "%d/%m/%Y %H:%M:%S") if str_in else None

        def apply(obj):
            obj.replace(np.nan, None)

            new_dfg = pd.DataFrame()
            new_dfg["timestamp"] = pd.to_datetime(
                obj["# Timestamp"], format="%d/%m/%Y %H:%M:%S"
            )
            new_dfg["mobile_type"] = (
                obj["Type of mobile"].astype(str).apply(apply_string_format)
            )
            new_dfg["mmsi"] = obj["MMSI"].astype(int)
            new_dfg["latitude"] = obj["Latitude"].astype(float)
            new_dfg["longitude"] = obj["Longitude"].astype(float)
            new_dfg["nav_stat"] = (
                obj["Navigational status"].astype(str).apply(apply_string_format)
            )
            new_dfg["rot"] = obj["ROT"].astype(float)
            new_dfg["sog"] = obj["SOG"].astype(float)
            new_dfg["cog"] = obj["COG"].astype(float)
            new_dfg["heading"] = obj["Heading"].astype(float)
            new_dfg["imo"] = obj["IMO"].astype(str).apply(apply_string_format)
            new_dfg["callsign"] = obj["Callsign"].astype(str).apply(apply_string_format)
            new_dfg["name"] = obj["Name"].astype(str).apply(apply_string_format)
            new_dfg["ship_type"] = (
                obj["Ship type"].astype(str).apply(apply_string_format)
            )
            new_dfg["cargo_type"] = (
                obj["Cargo type"].astype(str).apply(apply_string_format)
            )
            new_dfg["width"] = obj["Width"].astype(float)
            new_dfg["length"] = obj["Length"].astype(float)
            new_dfg["position_fixing_device_type"] = (
                obj["Type of position fixing device"]
                .astype(str)
                .apply(apply_string_format)
            )
            new_dfg["draught"] = obj["Draught"].astype(float)
            new_dfg["destination"] = (
                obj["Destination"].astype(str).apply(apply_string_format)
            )
            new_dfg["eta"] = obj["ETA"].astype(str).apply(apply_datetime_if_not_none)
            new_dfg["data_src_type"] = (
                obj["Data source type"].astype(str).apply(apply_string_format)
            )
            new_dfg["a"] = obj["A"].astype(float)
            new_dfg["b"] = obj["B"].astype(float)
            new_dfg["d"] = obj["D"].astype(float)
            new_dfg["c"] = obj["C"].astype(float)

            new_dfg.where(new_dfg.notnull(), None)

            return new_dfg

        print(csv_fname)

        d6tstack.combine_csv.CombinerCSV(
            [csv_fname], apply_after_read=apply, add_filename=False
        ).to_psql_combine(SqlConnector.cfg_uri_psql, "public.data", if_exists="append")
