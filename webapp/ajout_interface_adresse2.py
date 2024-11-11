# v5 indicateur de risque
# v4  avec ajout adresse
import streamlit as st
import pydeck as pdk
import xarray as xr
import os
import pandas as pd
import numpy as np
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

# Fonction pour extraire un titre pertinent basé sur le nom du fichier
def extract_title(filename):
    start = filename.find("_") + 1
    end = filename.find("-", start)
    return filename[start:end].replace("_", " ").capitalize()

# Fonction pour sélectionner le dégradé de couleur en fonction du nom de fichier
def select_theme(filename):
    filename = filename.lower()
    if "frost" in filename or "precipitation" in filename or "drought" in filename:
        # Dégradé progressif du bleu clair au bleu foncé
        return [
            [173, 216, 230, 50],  # Light blue with lower opacity
            [135, 206, 235, 100],
            [0, 191, 255, 150],
            [30, 144, 255, 200],
            [0, 0, 255, 220],     # Medium blue
            [0, 0, 139, 255],     # Dark blue
        ]
    elif "fire" in filename or "heat" in filename:
        # Dégradé progressif du rouge clair au rouge foncé
        return [
            [255, 182, 193, 50],  # Light pink with lower opacity
            [255, 99, 71, 100],
            [255, 69, 0, 150],
            [255, 0, 0, 200],
            [178, 34, 34, 220],   # Medium red
            [139, 0, 0, 255],     # Dark red
        ]
    elif "wind" in filename:
        # Dégradé progressif du vert clair au bleu-vert foncé
        return [
            [144, 238, 144, 50],  # Light green with lower opacity
            [60, 179, 113, 100],
            [32, 178, 170, 150],
            [0, 128, 128, 200],
            [0, 100, 0, 220],     # Medium green
            [0, 128, 255, 255],   # Dark blue-green
        ]
    else:
        # Thème par défaut rouge
        return [
            [255, 182, 193, 50],  # Light pink with lower opacity
            [255, 99, 71, 100],
            [255, 69, 0, 150],
            [255, 0, 0, 200],
            [178, 34, 34, 220],   # Medium red
            [139, 0, 0, 255],     # Dark red
        ]

# Fonction pour calculer le quintile d'une valeur donnée
def calculate_risk(value, quintiles):
    for i, q in enumerate(quintiles):
        if value <= q:
            return i + 1  # Risque de 1 à 5 basé sur le quintile
    return 5  # Si la valeur est plus grande que le dernier quintile, risque = 5

# Fonction pour obtenir l'indicateur de risque
def get_risk_value(ds, latitude, longitude):
    # Sélectionner la donnée pour le point spécifié en utilisant 'nearest' pour la latitude et la longitude
    point_data = ds.sel(lat=latitude, lon=longitude, method="nearest")
    
    # Extraire la valeur de la variable (en supposant que la variable d'intérêt est la première variable)
    # Si vous avez plusieurs variables dans votre dataset, vous devez préciser la variable que vous voulez.
    point_value = point_data.isel(time=0)  # Sélectionner la première dimension de temps (si plusieurs années)
    
    # Convertir en valeur numérique
    point_value = point_value.values  # Convertir en scalaire si besoin
    return point_value


# Dossier contenant les fichiers NetCDF
directory = "../data-collect/donnees_risk_climatique_telechargees/"
all_datasets, all_filenames = load_all_netcdf_files(directory)

st.title("Cartes des indicateurs climatiques")

# Sélection de l'année avec un slider
year = st.slider("Sélectionnez l'année", min_value=1979, max_value=2023, step=1, value =2021)

# Entrée utilisateur pour la latitude et la longitude
latitude = st.number_input("Entrez la latitude", value=50.0)
longitude = st.number_input("Entrez la longitude", value=2.0)

# Utilisation des onglets pour afficher chaque dataset dans une carte séparée
tabs = st.tabs([extract_title(filename) for filename in all_filenames])

for i, (ds, filename) in enumerate(zip(all_datasets, all_filenames)):
    with tabs[i]:
        # Sélection des données pour l'année choisie
        selected_data = ds.sel(time=str(year))

        # Convertir en DataFrame pour pydeck
        df = selected_data.to_dataframe().reset_index()

        # Vérifiez les colonnes présentes et utilisez la bonne colonne pour les poids
        weight_column = "precipitation" if "precipitation" in df.columns else df.columns[-1]

        # Couleur dynamique basée sur le thème
        color_range = select_theme(filename)
         
        risk = get_risk_value(ds, latitude, longitude)
        # Afficher l'indicateur de risque
        st.write(f"**Indicateur de risque pour les coordonnées ({latitude}, {longitude})**: {risk}/5")

        # Création du HeatmapLayer pour pydeck
        layer = pdk.Layer(
            "HeatmapLayer",
            data=df,
            get_position=["lon", "lat"],
            get_weight=weight_column,
            radiusPixels=30,
            opacity=0.4,
            colorRange=color_range,  # Appliquer la gamme de couleurs sélectionnée
        )
        # Point utilisateur
        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame({'lon': [longitude], 'lat': [latitude]}),
            get_position=["lon", "lat"],
            get_color=[255, 0, 0, 255],  #  rouge
            get_radius=10000,  # Augmentation de la taille du point
        )

        # Label affichant les coordonnées
        label_layer = pdk.Layer(
        "TextLayer",
        data=pd.DataFrame({'lon': [longitude], 'lat': [latitude], 'label': [f'({longitude}, {latitude})']}),  # Le label contient les coordonnées
        get_position=["lon", "lat"],
        get_text="label",  # Le texte à afficher
        get_size=15,  # Taille du texte
        get_color=[0, 0, 0, 255],  # Couleur blanche pour le texte
        get_alignment_baseline="'center'",  # Centrer le texte
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
            layers=[layer, point_layer, label_layer],
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/light-v9'
        )
        st.pydeck_chart(r)

        # Extraire et afficher la valeur du layer à la position de l'utilisateur
        value_at_point = selected_data.interp(lon=longitude, lat=latitude, method="nearest")[weight_column].values
        st.write(f"**Valeur de l'indicateur à l'emplacement sélectionné ({latitude}, {longitude})**: {value_at_point}")

        # Affichage de l'année sélectionnée et du nom du fichier
        st.write(f"**Année sélectionnée**: {year}")
        st.write(f"**Indicateur**: {extract_title(filename)}")
