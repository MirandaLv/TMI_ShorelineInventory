

# Utilizing the CO-OPS API to retrive information about all stations tide info in Chesapeake Bay

import os
import json
import math
from datetime import datetime, timedelta
from typing import Optional, Union

import pandas as pd
import requests
import geopandas as gpd
from shapely.geometry import Point


def get_stations_from_bbox(geofile):
    
    """Return a list of stations IDs found within a bounding box.
    Returns:
        GeoDataFrame[str]: A geodataframe with all stations' coordinates, id, and name
    """
    
    data_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    response = requests.get(data_url)
    json_dict = response.json()
    
    stations = []
    for station in json_dict["stations"]:
        station_info = []
        station_info.append(station['name'])
        station_info.append(station['id'])
        station_info.append(station['lat'])
        station_info.append(station['lng'])
        
        stations.append(station_info)
    
    df = pd.DataFrame(stations, columns=['name', 'id', 'lat', 'lng'])
    geometry = [Point(xy) for xy in zip(df.lng, df.lat)]
    points_gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
    
    bound_gdf = gpd.read_file(geofile, driver='GeoJSON')
    sub_gdf = points_gdf[points_gdf.within(bound_gdf.loc[0, 'geometry'])]
    
    return sub_gdf




begin_date = ''
end_date = ''
product_name = ''
datum = 'NAVD'
time_zone = ''
units = 'metric'


root_path = os.path.abspath('..')
bounding_file = os.path.join(root_path, 'data/boundary.geojson')

stations_df = get_stations_from_bbox(bounding_file)





