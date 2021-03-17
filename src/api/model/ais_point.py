from datetime import datetime


class AisPoint:
    def __init__(
            self,
            **kwargs,
    ):
        self.id = id
        self.course_id = kwargs['course_id'] if 'course_id' in kwargs else None
        self.timestamp = kwargs['timestamp']
        self.location = kwargs['location'] if 'location' in kwargs else [kwargs['longitude'], kwargs['latitude']]
        self.rot = kwargs['rot']
        self.sog = kwargs['sog']
        self.cog = kwargs['cog']
        self.heading = kwargs['heading']
        self.position_fixing_device_type = kwargs['position_fixing_device_type']
