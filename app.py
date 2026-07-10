import streamlit as st
import geopandas as gpd
import pandas as pd
import zipfile
import os
import folium
from folium.features import GeoJsonTooltip
from streamlit.components.v1 import html

# -------------------------------
# FULL SCREEN LAYOUT
# -------------------------------
st.set_page_config(layout="wide")

# -------------------------------
# PASTEL HEADER
# -------------------------------
st.markdown("""
<div style="
    background-color:#ffe6f2;
    padding:25px;
    border-radius:12px;
    box-shadow:0 2px 8px rgba(0,0,0,0.1);
    text-align:center;
">
    <h1 style="color:#b30086; font-size:36px; margin:0;">
        🌧️ Suriname — Impactzones Maximale Dagneerslag
    </h1>
    <p style="color:#66004d; font-size:18px; margin-top:10px;">
        15 km impactradius rond stations met hoogste dagneerslag
    </p>
</div>
""", unsafe_allow_html=True)

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
districts = districts.to_crs("EPSG:4326")

# -------------------------------
# 3. REGENVALDATA INLADEN
# -------------------------------
df = pd.read_excel("data/rainfall/Rainfall_Data_Suriname_2026.xlsx")

df = df.rename(columns={"Rainfall (mm)": "Rainfall_mm"})
df["Date"] = pd.to_datetime(df["Date"])
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# -------------------------------
# 4. SELECTIE JAAR + MAAND
# -------------------------------
year = st.selectbox("Kies jaar", sorted(df["Year"].unique()))
month = st.selectbox("Kies maand", sorted(df["Month"].unique()))

filtered = df[(df["Year"] == year) & (df["Month"] == month)]

if filtered.empty:
    st.warning("Geen data voor deze maand.")
    st.stop()

# -------------------------------
# 5. SPATIAL JOIN
# -------------------------------
stations = gpd.GeoDataFrame(
    filtered,
    geometry=gpd.points_from_xy(filtered["Longitude"], filtered["Latitude"]),
    crs="EPSG:4326"
)

joined = gpd.sjoin(stations, districts, how="left", predicate="within")

# -------------------------------
# 6. MAX PER DISTRICT
# -------------------------------
valid = joined.dropna(subset=["Rainfall_mm"])

if valid.empty:
    st.warning("Geen geldige neerslagdata beschikbaar.")
    max_points = pd.DataFrame()
else:
    idx = valid.groupby("DISTR_NAAM")["Rainfall_mm"].idxmax()
    max_points = valid.loc[idx]

# -------------------------------
# 7. IMPACTKLASSEN
# -------------------------------
def classify(r):
