import folium
from folium.plugins import HeatMap
import geopandas as gpd
import numpy as np
from modules.utils import ensure_shapefile_unzipped

def create_hazard_map(raster, lons, lats,
                      shapefile_folder="data/shapes",
                      shapefile_zip="data/shapes/Distrikten_AdjAOI.zip"):

    # Zorg dat shapefile beschikbaar is (werkt op Streamlit Cloud)
    ensure_shapefile_unzipped(shapefile_zip, shapefile_folder)

    shapefile_path = f"{shapefile_folder}/Distrikten_AdjAOI.shp"

    # Shapefile inladen
    gdf = gpd.read_file(shapefile_path)

    # Kaart centreren op Suriname
    center = [
        gdf.geometry.centroid.y.mean(),
        gdf.geometry.centroid.x.mean()
    ]

    m = folium.Map(location=center, zoom_start=7, tiles="cartodbpositron")

    # Raster omzetten naar HeatMap punten
    points = []
    for i in range(len(lats)):
        for j in range(len(lons)):
            points.append([lats[i], lons[j], float(raster[i, j])])

    HeatMap(
        points,
        radius=18,
        blur=25,
        max_zoom=7
    ).add_to(m)

    # Districten toevoegen
    folium.GeoJson(gdf).add_to(m)

    return m
