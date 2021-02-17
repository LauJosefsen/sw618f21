from dataclasses import dataclass
from datetime import datetime

from typing import Any

@dataclass
class AisDataEntry:
    timestamp: datetime
    mobile_type: str
    mmsi: int
    latitude: float
    longitude: float
    nav_stat: str
    rot: float
    sog: float
    cog: float
    heading: float
    imo: str
    callsign: str
    name: str
    ship_type: str
    cargo_type: str
    width: float
    length: float
    position_fixing_device_type: str
    draught: float
    destination: str
    eta: datetime
    data_src_type: str
    a: float
    b: float
    c: float
    d: float

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        timestamp = datetime.strptime(obj["timestamp"], "%d/%m/%Y %H:%M:%S")
        mobile_type = obj["mobile_type"]
        mmsi = int(obj["mmsi"])
        latitude = float(obj["latitude"])
        longitude = float(obj["longitude"])
        nav_stat = obj["nav_stat"]
        rot = float(obj["rot"]) if obj['rot'] else None
        sog = float(obj["sog"]) if obj['sog'] else None
        cog = float(obj["cog"]) if obj['cog'] else None
        heading = float(obj["heading"]) if obj['heading'] else None
        imo = obj["imo"]
        callsign = obj["callsign"]
        name = obj["name"]
        ship_type = obj["ship_type"]
        cargo_type = obj["cargo_type"]
        width = float(obj["width"]) if obj['width'] else None
        length = float(obj["length"]) if obj['length'] else None
        position_fixing_device_type = obj["position_fixing_device_type"]
        draught = float(obj["draught"]) if obj['draught'] else None
        destination = obj["destination"]
        eta = datetime.strptime(obj["eta"], "%d/%m/%Y %H:%M:%S") if obj["eta"] else None
        data_src_type = obj["data_src_type"]
        a = float(obj['a']) if obj["a"] else None
        b = float(obj['b']) if obj["b"] else None
        c = float(obj['c']) if obj["c"] else None
        d = float(obj['d']) if obj["d"] else None
        return AisDataEntry(timestamp, mobile_type, mmsi, latitude, longitude, nav_stat, rot, sog, cog, heading, imo,
                            callsign, name, ship_type, cargo_type, width, length, position_fixing_device_type, draught,
                            destination, eta, data_src_type, a, b, c, d)
