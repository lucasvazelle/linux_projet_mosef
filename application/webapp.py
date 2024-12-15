import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
from geopy.geocoders import Nominatim
import plotly.express as px
import numpy as np
from pathlib import Path
import base64
import os

# Configuration de la page
st.set_page_config(page_title="Climate Indicator", page_icon="🌍", layout="wide")


def find_file(filename, search_path="."):
    """
    Recherche un fichier dans un répertoire et ses sous-répertoires.
    Args:
        filename (str): Nom du fichier à rechercher.
        search_path (str): Chemin de départ pour la recherche.
    Returns:
        str: Chemin complet du fichier si trouvé, sinon None.
    """
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None


# Charger l'image de fond
image_path = find_file("green.jpg")
if not image_path:
    st.error("L'image de fond n'a pas été trouvée. Vérifiez son emplacement.")
else:
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        body, html, .main .block-container, .stApp {{
            color: white !important;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur lors de la lecture de l'image: {e}")


@st.cache_data
def load_data(file_name, variable_mapping=None):
    """
    Charge les données CSV et applique une préparation spécifique si nécessaire.
    Args:
        file_name (str): Nom du fichier CSV.
        variable_mapping (dict, optional): Mapping des colonnes (si applicable).
    Returns:
        pd.DataFrame: DataFrame préparé.
    """
    data_path = find_file(file_name)
    if not data_path:
        raise FileNotFoundError(f"Le fichier '{file_name}' est introuvable.")

    # Charger les données
    df = pd.read_csv(data_path)

    # Mapper les valeurs de "risk" et convertir en float
    risk_mapping = {"Low": 1, "Medium": 2, "High": 3}
    df["risk"] = df["risk"].map(risk_mapping).fillna(0)
    df["risk"] = df["risk"].astype(float)

    df["lat"] = df["lat"].round(2)
    df["lon"] = df["lon"].round(2)

    return df


def create_time_series(data, lat, lon, variable_name, title):
    """Crée un graphique temporel des données pour une localisation donnée avec fond noir"""
    try:
        # Filtrer les données pour la localisation spécifique
        location_data = data[(data["lat"] == lat) & (data["lon"] == lon)].sort_values(
            "year"
        )

        # Créer le graphique avec plotly
        fig = px.line(
            location_data,
            x="year",
            y=variable_name,
            title=title,
            labels={
                "year": "Year",
                variable_name: "Risk Level",
            },
        )

        # Personnaliser le layout pour fond noir et style général
        fig.update_layout(
            template="plotly_dark",  # Template avec fond noir
            hovermode="x unified",
            yaxis=dict(
                tickmode="array",
                ticktext=["Low", "Medium", "High"],
                tickvals=[1, 2, 3],
                gridcolor="gray",  # Couleur des lignes de la grille pour lisibilité
            ),
            xaxis=dict(
                gridcolor="gray"  # Couleur des lignes de la grille pour l'axe X
            ),
            title_font=dict(color="white"),  # Couleur du titre
            font=dict(color="white"),  # Couleur générale des textes
            paper_bgcolor="black",  # Fond extérieur
            plot_bgcolor="black",  # Fond du graphique
            showlegend=False,
        )

        return fig
    except Exception as e:
        st.error(f"Error while creating the chart: {str(e)}")
        return None


# Définir la fonction de géocodage
def get_coordinates(city, country):
    """
    Get the latitude and longitude coordinates of a given city and country.
    """
    geolocator = Nominatim(user_agent="my_climate_app")
    location = geolocator.geocode(f"{city}, {country}")

    if location:
        return round(location.point.latitude, 2), round(location.point.longitude, 2)
    else:
        return None, None


def generate_risk_badge(risk_level):
    if risk_level == 1:
        badge_html = """
                    <div style="padding: 10px; border-radius: 5px; background: #28a745; color: white; text-align: center; font-weight: bold;">
                        Low Risk (1)
                    </div>
                    """
    elif risk_level == 2:
        badge_html = """
                    <div style="padding: 10px; border-radius: 5px; background: #ffc107; color: black; text-align: center; font-weight: bold;">
                        Medium Risk (2)
                    </div>
                    """
    elif risk_level == 3:
        badge_html = """
                    <div style="padding: 10px; border-radius: 5px; background: #dc3545; color: white; text-align: center; font-weight: bold;">
                        High Risk (3)
                    </div>
                    """
    else:
        badge_html = """
                    <div style="padding: 10px; border-radius: 5px; background: gray; color: white; text-align: center; font-weight: bold;">
                        Unknown Risk
                    </div>
                    """
    return badge_html


# Charger les données
try:
    wind_data = load_data(
        "wind.csv", variable_mapping={"risk": {"Low": 1, "Medium": 2, "High": 3}}
    )
    precipitation_data = load_data("precipitation.csv")
except Exception as e:
    st.error(f"Erreur lors du chargement des données: {str(e)}")
    st.stop()


# Interface principale
col_legend, col_main = st.columns([1, 3])

with col_legend:
    st.markdown(
        """
    ### User Guide
    🌍 Select a country and city, then choose a year to view the data  
    🗺️ On the map, your selected city is marked with an orange point  
    📊 The graph shows the evolution of climate risks over time
    
    ### Risk Legend
    - <span style='color: #28a745;'>Low Risk (1) :</span> Minimal impact expected.
    - <span style='color: #ffc107;'>Medium Risk (2) :</span> Moderate impact possible.
    - <span style='color: #dc3545;'>High Risk (3) :</span> Significant impact likely.
    """,
        unsafe_allow_html=True,
    )

    with st.expander("ℹ️ About the application"):
        st.markdown(
            """
        ### 🌍 Global Vision
        Our climate risk prediction application is designed specifically for insurance professionals,
        enabling you to anticipate climate risks and refine your coverage strategies effectively.
        
        ### 📊 Indicators
        Analyzed indicators include:
        - **Extreme Precipatation**
        - **Extreme Winds**
        
        ### 📈 Data
        - Climate Data: CSV
        - Period: 2025-2035
        - Updates: Regular
        - Source : [Climate Data Store](https://cds.climate.copernicus.eu/datasets)
        
        ### 🚧 Features
        - Search by city
        - Visualization on interactive map
        - Risk calculation
        - Temporal analysis
                    
        ### 👥 Contacts:
        - Lucas Vazelle [🎓](https://www.linkedin.com/in/lucas-vazelle)
        - Mariam Tarverdian [🎓](https://www.linkedin.com/in/mariam-tarverdian-9a6140200)
        - Chahla Tarmoun [🎓](https://www.linkedin.com/in/chahla-tarmoun-4b546a160)
        - Aya Mokhtar [🎓](https://www.linkedin.com/in/aya-mokhtar810b4b216)
        """
        )
with col_main:
    # En-tête
    st.markdown(
        """
        <div class="title-container">
            <h1 style='text-align: center;'>🌡️ Climate Indicators Analysis</h1>
            <p style='text-align: center;'>Explore and analyze climate data from around the world</p>
        </div>
	<style>
       """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <style>
            /* Style pour les labels */
            .css-1c2pvh4 label, 
            .css-1b6tptk label, 
            .css-1n4l1t8 label, 
            .stTextInput label, 
            .stSelectbox label {
                color: #FFFFFF !important; /* Texte en blanc */
                font-size: 1rem; /* Taille de la police */
            }

        </style>
    """,
        unsafe_allow_html=True,
    )
    # Sélecteur d'année, pays et ville
    selected_year = st.selectbox("📅 Select a year", sorted(wind_data["year"].unique()))
    country_name = st.text_input("🔍 Enter a country (e.g., France)")
    city_name = st.text_input("🔍 Enter a city (e.g., Paris)")

    if country_name and city_name:
        city_lat, city_lon = get_coordinates(city_name, country_name)
        if city_lat and city_lon:
            st.markdown("### Coordinates of the Selected City")
            st.markdown(
                f"Latitude: <span class='highlight-coordinates'>{city_lat}</span><br>Longitude: <span class='highlight-coordinates'>{city_lon}</span>",
                unsafe_allow_html=True,
            )

            year_wind_data = wind_data[wind_data["year"] == selected_year]
            year_precipitation_data = precipitation_data[
                precipitation_data["year"] == selected_year
            ]

            nearest_wind_idx = (
                year_wind_data[["lat", "lon"]]
                .apply(
                    lambda x: ((x["lat"] - city_lat) ** 2 + (x["lon"] - city_lon) ** 2)
                    ** 0.5,
                    axis=1,
                )
                .idxmin()
            )
            nearest_precipitation_idx = (
                year_precipitation_data[["lat", "lon"]]
                .apply(
                    lambda x: ((x["lat"] - city_lat) ** 2 + (x["lon"] - city_lon) ** 2)
                    ** 0.5,
                    axis=1,
                )
                .idxmin()
            )

            nearest_wind_data = year_wind_data.loc[nearest_wind_idx]
            nearest_precipitation_data = year_precipitation_data.loc[
                nearest_precipitation_idx
            ]

            # Afficher les points de données les plus proches
            st.markdown("### Closest coordinates in our database")
            st.markdown(
                f"Nearest Latitude: <span class='highlight-closest'>{nearest_wind_data['lat']}</span><br>Nearest Longitude: <span class='highlight-closest'>{nearest_wind_data['lon']}</span>",
                unsafe_allow_html=True,
            )

            # Explication du niveau de risque
            # Fonction pour convertir le niveau de risque numérique en texte
            st.markdown(
                f"""
            📅 **Selected Year**: <span style='color: #ffa500; font-weight: bold;'>{selected_year}</span>
            """,
                unsafe_allow_html=True,
            )

            def get_risk_text(risk_value):
                if risk_value == 1:
                    return "Low"
                elif risk_value == 2:
                    return "Medium"
                elif risk_value == 3:
                    return "High"
                else:
                    return "Unknown"

            st.write("### Wind Risk Level of the Region")
            risk_text = get_risk_text(nearest_wind_data["risk"])
            st.markdown(
                f"""
            **This is the risk level for the selected region:** <span style='color: #ffcc00; font-weight: bold;'>{risk_text}</span>
            <br><br>
            **Number of extreme wind days per year in the selected region**: <span style='color: #ffa500; font-weight: bold;'>{nearest_wind_data['days']}</span>
            """,
                unsafe_allow_html=True,
            )
            risk_level = nearest_wind_data["risk"]  # Récupérer le niveau de risque
            risk_badge_html = generate_risk_badge(risk_level)
            st.markdown(risk_badge_html, unsafe_allow_html=True)

            st.write("### Precipitation Risk Level of the Region")
            risk_text2 = get_risk_text(nearest_precipitation_data["risk"])
            st.markdown(
                f"""
            **This is the risk level for the selected region:** <span style='color: #ffcc00; font-weight: bold;'>{risk_text2}</span>
            <br><br>
            **Number of extreme precipitation days per year in the selected region**: <span style='color: #ffa500; font-weight: bold;'>{nearest_precipitation_data['days']}</span>
            """,
                unsafe_allow_html=True,
            )
            risk_level2 = nearest_precipitation_data[
                "risk"
            ]  # Récupérer le niveau de risque
            risk_badge_html = generate_risk_badge(risk_level2)
            st.markdown(risk_badge_html, unsafe_allow_html=True)

            # Afficher le graphique temporel
            st.write("### Risk Evolution")

            time_series_fig = create_time_series(
                wind_data,
                nearest_wind_data["lat"],
                nearest_wind_data["lon"],
                "risk",
                "Wind Risk Over Time",
            )
            if time_series_fig is not None:
                st.plotly_chart(time_series_fig, use_container_width=True)

            time_series_fig2 = create_time_series(
                precipitation_data,
                nearest_precipitation_data["lat"],
                nearest_precipitation_data["lon"],
                "risk",
                "Precipitation Risk Over Time",
            )
            if time_series_fig2 is not None:
                st.plotly_chart(time_series_fig2, use_container_width=True)

            st.write("### Your location")

            m = folium.Map(location=[city_lat, city_lon], zoom_start=6)

            # Ajouter un maarqueur pour la ville sélectionnée
            folium.Marker(
                location=[city_lat, city_lon],
                popup=f"<b>{city_name}, {country_name}</b><br>Lat: {city_lat:.2f}<br>Lon: {city_lon:.2f}",
                icon=folium.Icon(color="orange", icon="info-sign"),
            ).add_to(m)

            # Afficher la carte dans Streamlit avec des dimensions adaptées
            st_folium(m, width=1050, height=800)  # Largeur et hauteur ajustées

        else:
            st.error("Sorry, coordinates for this city could not be found.")
    else:
        st.warning("Please enter both a country and a city.")
