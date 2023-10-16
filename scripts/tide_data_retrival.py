

# Utilizing the CO-OPS API to retrive information about all stations tide info in Chesapeake Bay

import os
import json
import math
from datetime import datetime, timedelta
from typing import Optional, Union

import pandas as pd
import requests
import geopandas as gpd

# referenced from https://github.com/GClunies/noaa_coops/blob/master/noaa_coops/station.py

def get_stations_from_bbox(
    lat_coords: list[float, float],
    lon_coords: list[float, float],
) -> list[str]:
    """Return a list of stations IDs found within a bounding box.

    Args:
        lat_coords (list[float]): The lower and upper latitudes of the box.
        lon_coords (list[float]): The lower and upper longitudes of the box.

    Raises:
        ValueError: lat_coords or lon_coords are not of length 2.

    Returns:
        list[str]: A list of station IDs.
    """
    station_list = []
    data_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    response = requests.get(data_url)
    json_dict = response.json()

    if len(lat_coords) != 2 or len(lon_coords) != 2:
        raise ValueError("lat_coords and lon_coords must be of length 2.")

    # Ensure lat_coords and lon_coords are in the correct order
    lat_coords = sorted(lat_coords)
    lon_coords = sorted(lon_coords)

    # if lat_coords[0] > lat_coords[1]:
    #     lat_coords[0], lat_coords[1] = lat_coords[1], lat_coords[0]

    # if lon_coords[0] > lon_coords[1]:
    #     lon_coords[0], lon_coords[1] = lon_coords[1], lon_coords[0]

    # Find stations in bounding box
    for station_dict in json_dict["stations"]:
        if lon_coords[0] < station_dict["lng"] < lon_coords[1]:
            if lat_coords[0] < station_dict["lat"] < lat_coords[1]:
                station_list.append(station_dict["id"])

    return station_list





station_id = '8638610'
begin_date = ''
end_date = ''
product_name = ''
datum = 'NAVD'
time_zone = ''
units = 'metric'

root_path = os.path.abspath('..')

print(root_path)
# polygons_file = os.path.join()
#
# gpd.read_file()




