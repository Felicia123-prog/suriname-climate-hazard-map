import folium
import geopandas as gpd
import numpy as np
from modules.utils import ensure_shapefile_unzipped

def create_hazard_map(raster, lons, lats,
                      shapefile_folder="data/shapes",
                      shapefile_zip="data/shapes/Distrikten_AdjAOI.zip"):

    # Zorg dat shapefile beschikbaar is (werkt op Streamlit Cloud)
    ensure_shapefile_unzipped(shapefile_zip, shapefile_folder)

    shapefile_path = f"{shapefile_folder}/Distrikten_AdjAOI.shp"

    gdf = gpd.read_file(shapefile_path)
    center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]

    m = folium.Map(location=center, zoom_start=7, tiles="cartodbpositron")

    # Raster naar punten
    points = []
    for i in range(len(lats)):
        for j in range(len(lons)):
            points.append([lats[i], lons[j], raster[i, j]])

    folium.plugins.HeatMap(
        [[p[0], p[1], p[2]] for p in points],
        radius=18,
        blur=25,
        max_zoom=7
    ).add_to(m)

    folium.GeoJson(gdf).add_to(m)

    return m
