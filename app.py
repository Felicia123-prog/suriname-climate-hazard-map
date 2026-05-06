import streamlit as st
import numpy as np
import geopandas as gpd

from modules.utils import load_rainfall_data, compute_monthly_totals, filter_month
from modules.interpolation import idw_interpolation
from modules.hazard_map import create_hazard_map

st.title("🌧️ Suriname Climate Hazard Map")
st.write("Interactieve GIS-kaart met maandelijkse neerslaginterpolatie.")

# Data inladen
df = load_rainfall_data()
monthly = compute_monthly_totals(df)

years = sorted(monthly["Year"].unique())
months = sorted(monthly["Month"].unique())

year = st.selectbox("Kies jaar", years)
month = st.selectbox("Kies maand", months)

filtered = filter_month(monthly, year, month)

if filtered.empty:
    st.warning("Geen data beschikbaar voor deze maand.")
    st.stop()

# Interpolatie grid
min_lon, max_lon = filtered["Longitude"].min(), filtered["Longitude"].max()
min_lat, max_lat = filtered["Latitude"].min(), filtered["Latitude"].max()

lons = np.linspace(min_lon, max_lon, 100)
lats = np.linspace(min_lat, max_lat, 100)
xi, yi = np.meshgrid(lons, lats)

raster = idw_interpolation(
    filtered["Longitude"].values,
    filtered["Latitude"].values,
    filtered["Rainfall"].values,
    xi, yi
)

# Kaart genereren
m = create_hazard_map(raster, lons, lats)

st.components.v1.html(m._repr_html_(), height=700)

