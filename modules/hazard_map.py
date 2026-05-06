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

    # Kaart centreren op Suriname
    center = [
        gdf.geometry.centroid.y.mean(),
        gdf.geometry.centroid.x.mean()
    ]

    m = folium.Map(location=center, zoom_start=7, tiles="cartodbpositron")

    # Raster normaliseren (belangrijk voor zichtbaarheid)
    raster = np.nan_to_num(raster, nan=0.0)
    rmin, rmax = raster.min(), raster.max()
    norm = (raster - rmin) / (rmax - rmin + 1e-9)

    # HeatMap punten genereren
    points = []
    for i in range(len(lats)):
        for j in range(len(lons)):
            lat = float(lats[i])
            lon = float(lons[j])
            val = float(norm[i, j])
            points.append([lat, lon, val])

    # HeatMap toevoegen
    HeatMap(
        points,
        radius=35,
        blur=45,
        max_zoom=7,
        min_opacity=0.6
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
