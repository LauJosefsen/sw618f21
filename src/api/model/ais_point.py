from datetime import datetime


class AisPoint:
    def __init__(
        self,
        id,
        mmsi,
        timestamp: datetime,
        location,
        rot,
        sog,
        cog,
        heading,
        ais_course_id=None,
    ):
        self.id = id
        self.mmsi = mmsi
        self.timestamp = timestamp
        self.location = location
        self.rot = rot
        self.sog = sog
        self.cog = cog
        self.heading = heading
        self.ais_course_id = ais_course_id
