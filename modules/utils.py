import pandas as pd
import os
import zipfile

def load_rainfall_data(folder_path="data/rainfall"):
    all_frames = []

    for file in os.listdir(folder_path):
        if file.endswith(".xlsx"):
            df = pd.read_excel(os.path.join(folder_path, file))
            all_frames.append(df)

    if not all_frames:
        return pd.DataFrame()

    df = pd.concat(all_frames, ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def compute_monthly_totals(df):
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    monthly = df.groupby(
        ["StationID", "Latitude", "Longitude", "Year", "Month"]
    )["Rainfall (mm)"].sum().reset_index()

    return monthly


def filter_month(df, year, month):
    return df[(df["Year"] == year) & (df["Month"] == month)]


def ensure_shapefile_unzipped(zip_path="data/shapes/Distrikten_AdjAOI.zip",
                              extract_to="data/shapes"):

    required = ["shp", "shx", "dbf", "prj"]
    base = "Distrikten_AdjAOI"

    if all(os.path.exists(f"{extract_to}/{base}.{ext}") for ext in required):
        return

    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP niet gevonden: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_to)
