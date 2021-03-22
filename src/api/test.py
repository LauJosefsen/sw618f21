#used for debugging
from datetime import datetime

from data_management.course_cluster import space_data_preprocessing
from model.ais_point import AisPoint

# space_data_preprocessing([
#     AisPoint(latitude=54.511778, longitude=11.503573, sog=16, timestamp=datetime.fromisoformat("2021-02-13 00:03:51"),
#              rot=0, cog=0, heading=0, position_fixing_device_type=""),
#     AisPoint(latitude=61.503407, longitude=11.498842, sog=16, timestamp=datetime.fromisoformat("2021-02-13 00:04:28"),
#              rot=0, cog=0, heading=0, position_fixing_device_type="")
# ])

space_data_preprocessing([
    AisPoint(latitude=54.410967, longitude=11.99546, sog=13, timestamp=datetime.fromisoformat("2021-02-13 21:15:14"),
             rot=0, cog=0, heading=0, position_fixing_device_type=""),
    AisPoint(latitude=54.410972, longitude=1.782088, sog=13, timestamp=datetime.fromisoformat("2021-02-13 21:15:24"),
             rot=0, cog=0, heading=0, position_fixing_device_type=""),
    AisPoint(latitude=54.410973, longitude=11.997512, sog=13, timestamp=datetime.fromisoformat("2021-02-13 21:15:34"),
             rot=0, cog=0, heading=0, position_fixing_device_type="")
])

# space_data_preprocessing([
#     AisPoint(latitude=55.471788, longitude=8.42337, sog=0, timestamp=datetime.fromisoformat("2021-02-13 00:00:10"),
#              rot=0, cog=0, heading=0, position_fixing_device_type=""),
#     AisPoint(latitude=55.471802, longitude=8.423362, sog=0, timestamp=datetime.fromisoformat("2021-02-13 00:01:10"),
#              rot=0, cog=0, heading=0, position_fixing_device_type="")
# ])
