import streamlit as st
import pydeck as pdk
import xarray as xr
import numpy as np
import pandas as pd
import os

# Fonction pour charger un fichier NetCDF
def load_netcdf_data(nc_file):
    return xr.open_dataset(nc_file, engine="netcdf4")

# Fonction pour charger tous les fichiers NetCDF d'un répertoire
def load_all_netcdf_files(directory):
    datasets = []
    filenames = []
    for filename in os.listdir(directory):
        if filename.endswith(".nc"):
            file_path = os.path.join(directory, filename)
            datasets.append(load_netcdf_data(file_path))
            filenames.append(filename)
    return datasets, filenames

# Répertoire contenant les fichiers NetCDF
directory = "../data-collect/donnees_risk_climatique_telechargees/"
all_datasets, all_filenames = load_all_netcdf_files(directory)

st.title("Carte des indicateurs climatiques")

# Sélection de l'année avec un slider
year = st.slider("Sélectionnez l'année", min_value=1979, max_value=2023, step=1)

# Utilisation des onglets pour afficher chaque dataset dans une carte séparée
tabs = st.tabs([f"Carte pour {filename}" for filename in all_filenames])

for i, ds in enumerate(all_datasets):
    with tabs[i]:
        # Sélection des données pour l'année choisie
        selected_data = ds.sel(time=str(year))

        # Convertir en DataFrame pour pydeck
        df = selected_data.to_dataframe().reset_index()

        # Vérifiez les colonnes présentes et utilisez la bonne colonne pour les poids (par exemple, précipitations ou autres)
        # Remplacez "variable_name" par la colonne réelle dans votre fichier NetCDF
        weight_column = "precipitation" if "precipitation" in df.columns else df.columns[-1]

        # Création du HeatmapLayer pour pydeck
        layer = pdk.Layer(
            "HeatmapLayer",
            data=df,
            get_position=["lon", "lat"],
            get_weight=weight_column,
            radiusPixels=30,
            opacity=0.4  # Ajuster l'opacité pour une meilleure visualisation
        )

        # Paramètres de vue de la carte
        view_state = pdk.ViewState(
            latitude=50,
            longitude=10,
            zoom=3,
            pitch=50,
        )

        # Créer et afficher la carte
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/light-v9'
        )
        st.pydeck_chart(r)

        # Affichage de l'année sélectionnée et du nom du fichier
        st.write(f"Année sélectionnée: {year}")
        st.write(f"Fichier: {all_filenames[i]}")
