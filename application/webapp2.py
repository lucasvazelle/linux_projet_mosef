import os 
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

# Configuration de la page
st.set_page_config(
    page_title="Climate Indicator",
    page_icon="🌍",
    layout="wide"
)

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

# Chercher le fichier image
image_path = find_file("fond.jpeg")

# Vérifiez si le fichier existe
if not image_path:
    st.error("L'image de fond n'a pas été trouvée. Vérifiez son emplacement.")
else:
    # Lire et encoder l'image en base64
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        # CSS pour définir l'image de fond
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        /* Appliquer une couleur blanche pour tout le texte */
        body, html, .main .block-container, .stApp {{
            color: white !important;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur lors de la lecture de l'image: {e}")
# Fonction pour charger et préparer les données
@st.cache_data  # Cache les données pour de meilleures performances

def load_data():
    """
    Charge les données de `wind.csv` où qu'il soit dans le projet.
    Returns:
        pd.DataFrame: DataFrame des données chargées.
    Raises:
        FileNotFoundError: Si le fichier `wind.csv` n'est pas trouvé.
    """
    # Rechercher le fichier partout dans le projet
    data_path = find_file("wind.csv")
    if not data_path:
        raise FileNotFoundError("Le fichier 'wind.csv' est introuvable. Veuillez vérifier son emplacement.")
    
    # Charger les données
    df = pd.read_csv(data_path)
    
    # Mapper les valeurs de "risk" et convertir en float
    risk_mapping = {
        "Low": 1,
        "Medium": 2,
        "High": 3
    }
    df['risk'] = df['risk'].map(risk_mapping).fillna(0)
    df['risk'] = df['risk'].astype(float)
    
    
    # Arrondir les valeurs de latitude et longitude
    df['lat'] = df['lat'].round(2)
    df['lon'] = df['lon'].round(2)
    
    return df

# Définir la fonction de création de graphique temporel
def create_time_series(data, lat, lon, variable_name):
    """Crée un graphique temporel des données pour une localisation donnée"""
    try:
        # Filtrer les données pour la localisation spécifique
        location_data = data[
            (data['lat'] == lat) & 
            (data['lon'] == lon)
        ].sort_values('year')
        
        # Créer le graphique avec plotly
        fig = px.line(
            location_data,
            x='year',
            y=variable_name,
            title=f"Risk Evolution at {lat:.2f}°N and {lon:.2f}°E",
            labels={
                'year': 'Year',
                variable_name: 'Risk Level',
            }
        )

        # Personnaliser le layout
        fig.update_layout(
            template="plotly_white",
            hovermode='x unified',
            yaxis=dict(
                tickmode='array',
                ticktext=['Low', 'Medium', 'High'],
                tickvals=[1, 2, 3]
            ),
            showlegend=False
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

# Charger les données
try:
    wind_data = load_data()
except Exception as e:
    st.error(f"Erreur lors du chargement des données: {str(e)}")
    st.stop()

# Créer deux colonnes : une pour la légende et une pour le contenu principal
col_legend, col_main = st.columns([1, 3])  # Modifié pour plus d'espace à droite

# Appliquer des styles CSS pour personnaliser les couleurs de fond des colonnes
st.markdown("""
    <style>
    /* Style général */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        /* Style pour les colonnes */
    html, body {
    background-color: white !important; /* Force le fond blanc */
    margin: 0; /* Supprime les marges par défaut */
    padding: 0; /* Supprime les paddings par défaut */
    height: 100%;
}

        /* Style pour la colonne principale */
        .css-1v3fvcr {
            background-color: #FFFFFF;
            padding: 20px;
            margin-left: 22%; /* Ajusté pour tenir compte de la largeur de la colonne légende */
        }
        
        /* Style pour les badges de risque */
        .risk-badge {
            padding: 12px 20px;
            border-radius: 8px;
            margin: 12px 0;
            color: white;
            text-align: center;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }

        .risk-badge:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }

        .risk-low {
            background: linear-gradient(135deg, #28a745, #20c997);
        }

        .risk-medium {
            background: linear-gradient(135deg, #ffc107, #fd7e14);
            color: black;
        }

        .risk-high {
            background: linear-gradient(135deg, #dc3545, #c82333);
        }

        /* Style pour les titres */
        h1 {
            color: #FFFFFF;
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid #FFFFFF;
        }

        h3 {
            color: #FFFFFF;
            font-size: 1.3em;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #E0E0E0;
        }

        /* Style pour les conteneurs de données */
        .data-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }

        .data-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        /* Style pour les cartes Folium */
        .stFolium {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        /* Style pour les graphiques Plotly */
        .js-plotly-plot {
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        /* Améliorations pour la légende */
        .legend-title {
            font-size: 1.4em;
            color: white;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid rgba(255,255,255,0.2);
        }

        .info-section {
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255,255,255,0.2);
        }

        .info-text {
            color: #FFFFFF;
            font-size: 0.9em;
            line-height: 1.6;
            margin-bottom: 0.8rem;
        }
    </style>
""", unsafe_allow_html=True)

def show_legend_and_info():
    """Affiche la légende et les informations dans la colonne de gauche."""
    st.markdown("""
    <div class="info-section">
    <h4 style='color: white; margin-bottom: 1rem;'>User Guide</h4>
    <p class="info-text">🎯 Select a year, a city and the country to visualize the data</p>
    <p class="info-text">🗺️ On the map:</p>
    <ul class="info-text">
    <li style='color: #FFFFFF;'>📍 City location</li>
    <li style='color: #FFFFFF;'>🎨 Data (color according to risk level)</li>
    </ul>
    <p class="info-text">📊 The graph shows the evolution of risks over time</p>
    </div>
    """, unsafe_allow_html=True)

# Utilisation de la fonction dans la colonne dédiée
with col_legend:
    show_legend_and_info()

    # Afficher la palette de couleurs des risques
    st.write("### Risk Level Legend")    
        # Display risk badges
    st.markdown('<div class="risk-badge risk-low">Low Risk (1)</div>', unsafe_allow_html=True)
    st.markdown('<div class="risk-badge risk-medium">Medium Risk (2)</div>', unsafe_allow_html=True)
    st.markdown('<div class="risk-badge risk-high">High Risk (3)</div>', unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("ℹ️ About the application"):
        st.markdown("""
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
        
        ### 🛠️ Features
        - Search by city
        - Visualization on interactive map
        - Risk calculation
        - Temporal analysis
                    
        ### 👥 Contacts:
        - Lucas Vazelle [💼](https://www.linkedin.com/in/lucas-vazelle)
        - Mariam Tarverdian [💼](https://www.linkedin.com/in/mariam-tarverdian-9a6140200)
        - Chahla Tarmoun [💼](https://www.linkedin.com/in/chahla-tarmoun-4b546a160)
        - Aya Mokhtar [💼](https://www.linkedin.com/in/aya-mokhtar810b4b216)
        """)
# Dans la colonne principale, afficher le contenu de l'application
with col_main:
    # En-tête
    st.markdown("""
        <div class="title-container">
            <h1 style='text-align: center;'>🌡️ Climate Indicators Analysis</h1>
            <p style='text-align: center;'>Explore and analyze climate data from around the world. </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
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
    """, unsafe_allow_html=True)
        
    # Sélecteur d'année
    selected_year = st.selectbox("📅 Select the year please", sorted(wind_data['year'].unique()))
    year_mask = (wind_data['year'] == selected_year)
    year_data = wind_data.loc[year_mask]

    # Sélecteur de ville et de pays
    city_name = st.text_input("🔍 Search for a city")
    country_name = st.text_input("🔍 Search for a country")

    if city_name and country_name:
        city_lat, city_lon = get_coordinates(city_name, country_name)
        
        st.write("### Coordinates found by Geopy:")
        st.write(f"Latitude: {city_lat}")
        st.write(f"Longitude: {city_lon}")
        
        if city_lat and city_lon:
            # Trouver les données les plus proches dans le dataframe
            nearest_idx = year_data[['lat', 'lon']].apply(lambda x: ((x['lat'] - city_lat)**2 + (x['lon'] - city_lon)**2)**0.5, axis=1).idxmin()
            nearest_data = year_data.loc[nearest_idx]
            
            # Déterminer le niveau de risque
            risk_level = nearest_data['risk']
            risk_text = "Low" if risk_level == 1 else "Medium" if risk_level == 2 else "High" if risk_level == 3 else "Unknown"
            risk_color = "risk-low" if risk_level == 1 else "risk-medium" if risk_level == 2 else "risk-high" if risk_level == 3 else ""

            st.write("### Risk Level for selected city:")
            st.markdown(f'<div class="risk-badge {risk_color}">{risk_text} Risk</div>', unsafe_allow_html=True)
            st.write("### Closest data points in the DataFrame:")
            st.write(f"Nearest Latitude: {nearest_data['lat']}")
            st.write(f"Nearest Longitude: {nearest_data['lon']}")
            
            # Afficher toutes les lignes correspondant à ces coordonnées
            matching_data = year_data[
                (year_data['lat'] == nearest_data['lat']) & 
                (year_data['lon'] == nearest_data['lon'])
            ]
            
            # Créer la carte avec des marqueurs colorés selon le niveau de risque
            m = folium.Map(location=[city_lat, city_lon], zoom_start=8)
            
            # Marker pour la ville recherchée
            folium.Marker(
                location=[city_lat, city_lon],
                popup=f"Ville: {city_name}, {country_name}",
                icon=folium.Icon(color='blue')
            ).add_to(m)
            
            # Marker pour le point de données le plus proche avec couleur selon le risque
            marker_color = 'green' if risk_level == 1 else 'orange' if risk_level == 2 else 'red' if risk_level == 3 else 'gray'
            folium.Marker(
                location=[nearest_data['lat'], nearest_data['lon']],
                popup=f"Latitude: {nearest_data['lat']:.2f}, Longitude: {nearest_data['lon']:.2f}<br>Risque: {risk_text}",
                icon=folium.Icon(color=marker_color)
            ).add_to(m)
            
            st.write(f"📅 Selected year: {selected_year}")
            st.write(f"Number of wind days for {city_name}, {country_name} in {selected_year}: {nearest_data['days']}")
            
            # Afficher le graphique temporel
            st.write("### Risk Evolution:")
                # Afficher le graphique temporel avec toutes les données
        time_series_fig = create_time_series(wind_data, nearest_data['lat'], nearest_data['lon'], 'risk')
        if time_series_fig is not None:
            st.plotly_chart(time_series_fig, use_container_width=True)
            
            st_folium(m, width=725)
        else:
            st.error("Sorry, coordinates for this city could not be found.")
