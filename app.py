import streamlit as st
import geopandas as gpd
import zipfile
import os

st.title("📂 Shapefile Kolommen Checker (ZIP Fix)")

# --- Pad naar jouw ZIP ---
zip_path = "data/shapes/Distrikten_AdjAOI.zip"
extract_dir = "data/shapes/extracted"

# --- Stap 1: ZIP uitpakken ---
if not os.path.exists(extract_dir):
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

st.success("ZIP uitgepakt!")

# --- Stap 2: Zoek de shapefile (.shp) ---
shp_file = None
for root, dirs, files in os.walk(extract_dir):
    for f in files:
        if f.endswith(".shp"):
            shp_file = os.path.join(root, f)

if shp_file is None:
    st.error("Geen .shp bestand gevonden in de ZIP!")
    st.stop()

st.write("📌 Gevonden shapefile:", shp_file)

# --- Stap 3: Shapefile inladen ---
try:
    gdf = gpd.read_file(shp_file)
    st.success("Shapefile succesvol geladen!")

    st.write("### 📌 Kolommen in jouw shapefile:")
    st.write(gdf.columns)

    st.write("### 📌 Eerste 5 rijen:")
    st.write(gdf.head())

except Exception as e:
    st.error(f"Fout bij het laden van de shapefile: {e}")
