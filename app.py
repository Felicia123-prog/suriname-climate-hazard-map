import streamlit as st
import streamlit.components.v1 as components
import numpy as np

from modules.utils import (
    load_rainfall_data,
    compute_monthly_totals,
    filter_month,
    ensure_shapefile_unzipped
)
from modules.interpolation import rbf_interpolation
from modules.hazard_map import create_hazard_map

st.title("🌧️ Suriname Climate Hazard Map")
st.write("Interactieve GIS-kaart met maandelijkse neerslaginterpolatie (RBF).")

# Shapefile klaarzetten
ensure_shapefile_unzipped()

# Data inladen
df = load_rainfall_data()
monthly = compute_monthly_totals(df)

# Dropdowns
years = sorted(monthly["Year"].unique())
months = sorted(monthly["Month"].unique())

year = st.selectbox("Kies jaar", years)
month = st.selectbox("Kies maand", months)

filtered = filter_month(monthly, year, month)

if filtered.empty:
    st.warning("Geen data beschikbaar voor deze maand.")
    st.stop()

# Interpolatie grid bepalen op basis van jouw stations
min_lon, max_lon = filtered["Longitude"].min(), filtered["Longitude"].max()
min_lat, max_lat = filtered["Latitude"].min(), filtered["Latitude"].max()

# Fijn grid voor vloeiende RBF
lons = np.linspace(min_lon, max_lon, 150)
lats = np.linspace(min_lat, max_lat, 150)
xi, yi = np.meshgrid(lons, lats)

# RBF INTERPOLATIE uitvoeren
raster = rbf_interpolation(
    filtered["Longitude"].values,
    filtered["Latitude"].values,
    filtered["Rainfall (mm)"].values,
    xi, yi
)

# Kaart genereren (met automatische zoom op jouw data)
m = create_hazard_map(raster, lons, lats)

# FOLIUM HTML TONEN — ENIGE METHODE DIE WERKT OP STREAMLIT CLOUD
components.html(
    m._repr_html_(),
    height=700,
    scrolling=True
)
