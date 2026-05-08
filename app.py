import streamlit as st
import geopandas as gpd

st.title("🔍 Shapefile Kolommen Checker")

st.write("We lezen nu jouw district-shapefile in om te zien welke kolommen erin zitten.")

# ---- LAAD DE DISTRICT SHAPEFILE ----
try:
    gdf = gpd.read_file("data/shapes/Distrikten_AdjAOI.shp")
    st.success("Shapefile succesvol geladen!")
    
    # Toon kolomnamen
    st.write("### 📌 Kolommen in jouw shapefile:")
    st.write(gdf.columns)

    # Toon eerste rijen zodat we de structuur zien
    st.write("### 📌 Eerste 5 rijen:")
    st.write(gdf.head())

except Exception as e:
    st.error(f"Fout bij het laden van de shapefile: {e}")
