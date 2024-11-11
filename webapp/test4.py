import streamlit as st
import pydeck as pdk
import xarray as xr
import numpy as np
import pandas as pd


def load_netcdf_data(nc_file):
    return xr.open_dataset(nc_file, engine = "netcdf4")

fichier_nc = '../data-collect/donnees_risk_climatique_telechargees/15_frequency_of_extreme_precipitation-reanalysis-yearly-grid-1940-2023-v1.0.nc'
ds = load_netcdf_data(fichier_nc)



st.title("Carte des précipitations extrêmes")
year = st.slider("Sélectionnez l'année", min_value=1940, max_value=2023, step=1)

selected_data = ds.sel(time=str(year))

df = selected_data.to_dataframe().reset_index()

layer = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position=["lon", "lat"],
    get_weight="data",
    radiusPixels=30,
    opacity=0.4  # Adjust the opacity for better visualization
)

# Set the viewport location
view_state = pdk.ViewState(
    latitude=50,
    longitude=10,
    zoom=3,
    pitch=50,
)

# Render the deck.gl map with the heatmap layer
r = pdk.Deck(layers=[layer], initial_view_state=view_state, map_style='mapbox://styles/mapbox/light-v9')
st.pydeck_chart(r)

# Display the selected year
st.write(f"Année sélectionnée: {year}")
