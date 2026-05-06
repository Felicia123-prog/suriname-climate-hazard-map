import pandas as pd
import os
import zipfile

def load_rainfall_data(folder_path="data/rainfall"):
    """Leest alle Excel-bestanden in de rainfall map in en combineert ze."""
    all_frames = []

    for file in os.listdir(folder_path):
        if file.endswith(".xlsx"):
            df = pd.read_excel(os.path.join(folder_path, file))
            all_frames.append(df)

    if not all_frames:
        return pd.DataFrame()

    df = pd.concat(all_frames, ignore_index=True)

    # Zorg dat Date een datetime is
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


def compute_monthly_totals(df):
    """Zet dagelijkse data om naar maandtotalen per station."""
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    # BELANGRIJK: juiste kolomnaam gebruiken
    monthly = df.groupby(
        ["StationID", "Latitude", "Longitude", "Year", "Month"]
    )["Rainfall (mm)"].sum().reset_index()

    return monthly


def filter_month(df, year, month):
    """Filtert op jaar en maand."""
    return df[(df["Year"] == year) & (df["Month"] == month)]


def ensure_shapefile_unzipped(zip_path="data/shapes/Distrikten_AdjAOI.zip",
                              extract_to="data/shapes"):
    """Zorgt dat de shapefile uitgepakt is op Streamlit Cloud."""
    required_files = [
        "Distrikten_AdjAOI.shp",
        "Distrikten_AdjAOI.shx",
        "Distrikten_AdjAOI.dbf",
        "Distrikten_AdjAOI.prj"
    ]

    # Check of shapefile al uitgepakt is
    if all(os.path.exists(os.path.join(extract_to, f)) for f in required_files):
        return

    # Als ZIP niet bestaat → foutmelding
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP niet gevonden: {zip_path}")

    # Uitpakken
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_to)
