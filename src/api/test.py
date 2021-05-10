from datetime import datetime

from ais_app.services.space_data_preprocessing_service import SpaceDataPreprocessingService

pointA = {"timestamp": datetime.fromisoformat("2021-03-22 03:21:09"),"latitude": 54.934558, "longitude": 11.805847, "sog":102.2}
pointB = {"timestamp": datetime.fromisoformat("2021-03-22 03:26:17"),"latitude": 55.788923, "longitude": 9.95265, "sog":74.9}


service = SpaceDataPreprocessingService()

print(service.calc_difference_value(pointA, pointB))
