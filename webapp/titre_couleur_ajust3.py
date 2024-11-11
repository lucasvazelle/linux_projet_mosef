import streamlit as st
import pydeck as pdk
import xarray as xr
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

# Dossier contenant les fichiers NetCDF
directory = "../data-collect/donnees_risk_climatique_telechargees/"
all_datasets, all_filenames = load_all_netcdf_files(directory)

st.title("Cartes des indicateurs climatiques")

# Sélection de l'année avec un slider
year = st.slider("Sélectionnez l'année", min_value=1979, max_value=2023, step=1, value=2023)

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
        st.write(f"**Année sélectionnée**: {year}")
        st.write(f"**Indicateur**: {extract_title(filename)}")
