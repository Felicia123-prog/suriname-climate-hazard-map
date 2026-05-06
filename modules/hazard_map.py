import folium
from folium.plugins import HeatMap
import geopandas as gpd
import numpy as np
from modules.utils import ensure_shapefile_unzipped

def create_hazard_map(raster, lons, lats,
                      shapefile_folder="data/shapes",
                      shapefile_zip="data/shapes/Distrikten_AdjAOI.zip"):

    ensure_shapefile_unzipped(shapefile_zip, shapefile_folder)

    shapefile_path = f"{shapefile_folder}/Distrikten_AdjAOI.shp"
    gdf = gpd.read_file(shapefile_path)

    # Bepaal bounding box van jouw data
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    # Center van jouw stations
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    # Automatische zoom (werkt heel goed)
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles="cartodbpositron")

    # Raster normaliseren
    raster = np.nan_to_num(raster, nan=0.0)
    rmin, rmax = raster.min(), raster.max()
    norm = (raster - rmin) / (rmax - rmin + 1e-9)

    # Heatmap punten
    points = []
    for i in range(len(lats)):
        for j in range(len(lons)):
            points.append([float(lats[i]), float(lons[j]), float(norm[i, j])])

    HeatMap(
        points,
        radius=30,
        blur=40,
        max_zoom=12,
        min_opacity=0.5
    ).add_to(m)

    # Districten overlay
    folium.GeoJson(
        gdf,
        style_function=lambda x: {
            "fillOpacity": 0,
            "color": "black",
            "weight": 1
        }
    ).add_to(m)

    return m
