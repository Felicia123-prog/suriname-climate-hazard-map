import streamlit as st
import geopandas as gpd
import pandas as pd
import zipfile
import os
import folium
from folium.features import GeoJsonTooltip
from streamlit.components.v1 import html

st.title("🌧️ Suriname Klimaat Impactkaart (Max dagneerslag per district)")

# -------------------------------
# 1. ZIP UITPAKKEN
# -------------------------------
zip_path = "data/shapes/Distrikten_AdjAOI.zip"
extract_dir = "data/shapes/extracted"

if not os.path.exists(extract_dir):
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

# Zoek shapefile
shp_file = None
for root, dirs, files in os.walk(extract_dir):
    for f in files:
        if f.endswith(".shp"):
            shp_file = os.path.join(root, f)

if shp_file is None:
    st.error("Geen shapefile gevonden!")
    st.stop()

# -------------------------------
# 2. SHAPEFILE INLADEN
# -------------------------------
districts = gpd.read_file(shp_file)
districts = districts.to_crs("EPSG:4326")  # CRS fix

# -------------------------------
# 3. REGENVALDATA INLADEN
# -------------------------------
df = pd.read_excel("data/rainfall/Rainfall_Data_Suriname_2026.xlsx")

# Kolom hernoemen zodat we een uniforme naam hebben
df = df.rename(columns={
    "Rainfall (mm)": "Rainfall_mm"
})

df["Date"] = pd.to_datetime(df["Date"])
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Day"] = df["Date"].dt.day

# -------------------------------
# 4. SELECTIE JAAR + MAAND
# -------------------------------
years = sorted(df["Year"].unique())
months = sorted(df["Month"].unique())

year = st.selectbox("Kies jaar", years)
month = st.selectbox("Kies maand", months)

filtered = df[(df["Year"] == year) & (df["Month"] == month)]

if filtered.empty:
    st.warning("Geen data voor deze maand.")
    st.stop()

# -------------------------------
# 5. SPATIAL JOIN (stations → districten)
# -------------------------------
stations = gpd.GeoDataFrame(
    filtered,
    geometry=gpd.points_from_xy(filtered["Longitude"], filtered["Latitude"]),
    crs="EPSG:4326"
)

joined = gpd.sjoin(stations, districts, how="left", predicate="within")

# -------------------------------
# 6. MAX DAGNEERSLAG PER DISTRICT
# -------------------------------
impact = (
    joined.groupby("DISTR_NAAM")["Rainfall_mm"]
    .max()
    .reset_index()
    .rename(columns={"Rainfall_mm": "MaxRain"})
)

# -------------------------------
# 7. IMPACTCATEGORIEËN
# -------------------------------
def classify(r):
    if pd.isna(r):
        return "Geen data"
    if r <= 25:
        return "Laag"
    elif r <= 75:
        return "Matig"
    elif r <= 150:
        return "Hoog"
    else:
        return "Extreem"

impact["ImpactClass"] = impact["MaxRain"].apply(classify)

# -------------------------------
# 8. MERGE MET DISTRICT POLYGONEN
# -------------------------------
districts_impact = districts.merge(impact, on="DISTR_NAAM", how="left")

# -------------------------------
# 9. KAART MAKEN
# -------------------------------
m = folium.Map(location=[5.8, -55.2], zoom_start=7)

folium.Choropleth(
    geo_data=districts_impact,
    data=districts_impact,
    columns=["DISTR_NAAM", "MaxRain"],
    key_on="feature.properties.DISTR_NAAM",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.4,
    nan_fill_color="lightgray",
    legend_name="Max dagneerslag (mm)"
).add_to(m)

# Tooltip
folium.GeoJson(
    districts_impact,
    tooltip=GeoJsonTooltip(
        fields=["DISTR_NAAM", "MaxRain", "ImpactClass"],
        aliases=["District", "Max regen (mm)", "Impact"],
        localize=True
    )
).add_to(m)

# -------------------------------
# 10. TONEN IN STREAMLIT
# -------------------------------
html(m._repr_html_(), height=700)
