import streamlit as st
import geopandas as gpd
import pandas as pd
import zipfile
import os
import folium
from folium.features import GeoJsonTooltip
from folium.plugins import ScaleBar
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
    if r <= 25: return "Laag"
    elif r <= 75: return "Matig"
    elif r <= 150: return "Hoog"
    else: return "Extreem"

max_points["ImpactClass"] = max_points["Rainfall_mm"].apply(classify)

impact_colors = {
    "Laag": "green",
    "Matig": "yellow",
    "Hoog": "orange",
    "Extreem": "red"
}

# -------------------------------
# 8. KAART
# -------------------------------
m = folium.Map(location=[5.8, -55.2], zoom_start=7)

# Schaalbalk
ScaleBar(position="bottomleft").add_to(m)

# North arrow
north_arrow = """
<div style="
position: fixed;
top: 120px;
left: 40px;
z-index: 9999;
">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/North_arrow.svg/120px-North_arrow.svg.png"
     width="60">
</div>
"""
m.get_root().html.add_child(folium.Element(north_arrow))

# -------------------------------
# 9. IMPACTCIRKELS
# -------------------------------
radius_m = 15000

for _, row in max_points.iterrows():
    lat = row["Latitude"]
    lon = row["Longitude"]
    mm = row["Rainfall_mm"]
    district = row["DISTR_NAAM"]
    station = row["StationID"]
    impact = row["ImpactClass"]
    color = impact_colors[impact]

    popup_html = (
        f"<b>{district}</b><br>"
        f"Station: {station}<br>"
        f"Impact: {impact}<br>"
        f"Max: {mm} mm<br>"
        f"Locatie: {lat:.4f}, {lon:.4f}"
    )

    # Cirkel
    folium.Circle(
        location=[lat, lon],
        radius=radius_m,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.15,
        popup=popup_html
    ).add_to(m)

    # Punt
    folium.CircleMarker(
        location=[lat, lon],
        radius=8,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        tooltip=f"{mm} mm"
    ).add_to(m)

# -------------------------------
# 10. LEGENDA
# -------------------------------
legend_html = """
<div style="
position: fixed;
bottom: 40px;
right: 40px;
z-index:9999;
background-color: #fff0f7;
padding: 15px;
border-radius: 10px;
box-shadow: 0 2px 8px rgba(0,0,0,0.2);
">
<b style="color:#b30086;">Impact Legenda</b><br>
<span style="color:green;">● Laag</span><br>
<span style="color:yellow;">● Matig</span><br>
<span style="color:orange;">● Hoog</span><br>
<span style="color:red;">● Extreem</span>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# -------------------------------
# 11. TONEN
# -------------------------------
html(m._repr_html_(), height=900, width="100%")
