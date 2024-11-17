import streamlit as st
import pydeck as pdk
import xarray as xr
import numpy as np
import pandas as pd

# Chargement du fichier NetCDF avec mise en cache
@st.cache_data
def load_netcdf_data(nc_file):
    return xr.open_dataset(nc_file, engine = "netcdf4")

# Chargement du fichier NetCDF
fichier_nc = '../data-collect/donnees_risk_climatique_telechargees/15_frequency_of_extreme_precipitation-reanalysis-yearly-grid-1940-2023-v1.0.nc'
ds = load_netcdf_data(fichier_nc)

# Extraire les données de précipitations et les coordonnées (lat, lon)
def get_precipitation_data(year):
    # Trouver l'index de l'année
    index = ds.time.dt.year == year
    # Sélectionner les précipitations pour l'année donnée
    precip_data = ds.data.sel(time=index).squeeze()
    # Extraire les latitudes et longitudes
    lats, lons = np.meshgrid(ds.lat.values, ds.lon.values)
    
    # Aplatir les tableaux pour aligner les données
    lats = lats.flatten()
    lons = lons.flatten()
    precip_data = precip_data.values.flatten()
    
    
    
    # Créer un DataFrame avec les données de position et les précipitations
    df = pd.DataFrame({
        "latitude": lats,
        "longitude": lons,
        "precipitation": precip_data
    })
    return df

# Fonction pour générer le layer pydeck pour les précipitations
def create_precipitation_layer(df):
    return pdk.Layer(
        "HexagonLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_radius=200,
        elevation_scale=4,
        elevation_range=[0, 1000],
        extruded=True,
        pickable=True,
        opacity=0.5,
        get_fill_color="[255, (precipitation / 100) * 255, 0]",
    )

# Interface utilisateur Streamlit
st.title("Visualisation des précipitations par année")

# Sélection de l'année
min_year = int(ds.time.dt.year.min())
max_year = int(ds.time.dt.year.max())
annee = st.slider("Sélectionnez l'année :", min_year, max_year, step=1)

# Obtenir les données de précipitations pour l'année sélectionnée
precip_data = get_precipitation_data(annee)

# Créer un layer pydeck avec les données de précipitations
precip_layer = create_precipitation_layer(precip_data)

# Affichage de la carte pydeck
st.pydeck_chart(
    pdk.Deck(
        map_style="light",
        initial_view_state={
            "latitude": precip_data["latitude"].mean(),
            "longitude": precip_data["longitude"].mean(),
            "zoom": 4,
            "pitch": 50,
        },
        layers=[precip_layer],
    )
)
