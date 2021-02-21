from dataclasses import dataclass
from datetime import datetime


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
