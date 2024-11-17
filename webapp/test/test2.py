import streamlit as st
import pydeck as pdk
import xarray as xr
import numpy as np
import pandas as pd

# Chargement du fichier NetCDF avec mise en cache
def load_netcdf_data(nc_file):
    return xr.open_dataset(nc_file, engine = "netcdf4")

# Chargement du fichier NetCDF
fichier_nc = '../data-collect/donnees_risk_climatique_telechargees/15_frequency_of_extreme_precipitation-reanalysis-yearly-grid-1940-2023-v1.0.nc'
ds = load_netcdf_data(fichier_nc)

# Create a Streamlit app to display the map with a slider for the years
st.title("Carte des précipitations extrêmes")

# Slider for selecting the year
year = st.slider("Sélectionnez l'année", min_value=1940, max_value=2023, step=1)

# Filter the dataset for the selected year
selected_data = ds.sel(time=str(year))

# Convert the selected data to a DataFrame for use with PyDeck
df = selected_data.to_dataframe().reset_index()

# Create a PyDeck layer
layer = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position=["lon", "lat"],
    get_weight="data",
    radiusPixels=30,
)

# Set the viewport location
view_state = pdk.ViewState(
    latitude=50,
    longitude=10,
    zoom=3,
    pitch=50,
)

# Render the deck.gl map
r = pdk.Deck(layers=[layer], initial_view_state=view_state)
st.pydeck_chart(r)
# Display the selected year
st.write(f"Année sélectionnée: {year}")

# Display the dataset information
st.write("Informations sur le dataset:")
st.write(ds)
