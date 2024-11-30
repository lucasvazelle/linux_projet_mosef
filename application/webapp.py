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

# Définir le chemin de l'image
image_path = Path("application/green.jpg")

# Vérifiez si le fichier existe
if not image_path.is_file():
    st.error("L'image de fond n'a pas été trouvée. Vérifiez le chemin.")
else:
    # Lire et encoder l'image en base64
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
        color: white !important;
        padding-top: 0;
        background-color: #333333;
    }}
    
    /* Appliquer une couleur blanche pour tout le texte */
    .css-1c2pvh4 label, 
    .css-1b6tptk label, 
    .css-1n4l1t8 label, 
    .stTextInput label, 
    .stSelectbox label, 
    .title-container, 
    .info-section, 
    .legend-title, 
    .info-text {{
        color: white !important;
    }}
    .highlight-coordinates {{
        color: #ffa500;
        font-weight: bold;
    }}
    .highlight-closest {{
        color: #ff6347;
        font-weight: bold;
    }}
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)


# Fonction pour charger et préparer les données
@st.cache_data  # Cache les données pour de meilleures performances
def load_data():
    # Charger les données
    data_path = "data_process/wind.csv"
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

# Utilisation de la fonction dans la colonne dédiée
with col_legend:
    # Afficher la légende et les informations
    st.markdown("""
    ### User Guide
    🌍 Select a country and city, then choose a year to view the data  
    🗺️ On the map, your selected city is marked with an orange point  
    📊 The graph shows the evolution of climate risks over time
    
    ### Risk Legend
    - <span style='color: #28a745;'>Low Risk (1) :</span> Minimal impact expected.
    - <span style='color: #ffc107;'>Medium Risk (2) :</span> Moderate impact possible.
    - <span style='color: #dc3545;'>High Risk (3) :</span> Significant impact likely.
    """, unsafe_allow_html=True)
    
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
        """)

# Dans la colonne principale, afficher le contenu de l'application
with col_main:
    # En-tête
    st.markdown("""
        <div class="title-container">
            <h1 style='text-align: center;'>🌡️ Climate Indicators Analysis</h1>
            <p style='text-align: center;'>Explore and analyze climate data from around the world</p>
        </div>
    """, unsafe_allow_html=True)

    # Sélecteur d'année
    selected_year = st.selectbox("📅 Select a year", sorted(wind_data['year'].unique()))
    year_mask = (wind_data['year'] == selected_year)
    year_data = wind_data.loc[year_mask]

    # Sélecteur de pays et de ville (avec meilleure guidance)
    country_name = st.text_input("🔍 Enter a country (e.g., France)")
    city_name = st.text_input("🔍 Enter a city (e.g., Paris)")

    if country_name and city_name:
        city_lat, city_lon = get_coordinates(city_name, country_name)

        if city_lat and city_lon:
            # Afficher les coordonnées trouvées par Geopy
            st.markdown("### Coordinates of the Selected City:")
            st.markdown(f"Latitude: <span class='highlight-coordinates'>{city_lat}</span><br>Longitude: <span class='highlight-coordinates'>{city_lon}</span>", unsafe_allow_html=True)
            
            # Trouver les données les plus proches dans le dataframe
            nearest_idx = year_data[['lat', 'lon']].apply(lambda x: ((x['lat'] - city_lat)**2 + (x['lon'] - city_lon)**2)**0.5, axis=1).idxmin()
            nearest_data = year_data.loc[nearest_idx]
            
            # Afficher les points de données les plus proches
            st.markdown("### Closest Data Points in the DataFrame:")
            st.markdown(f"Nearest Latitude: <span class='highlight-closest'>{nearest_data['lat']}</span><br>Nearest Longitude: <span class='highlight-closest'>{nearest_data['lon']}</span>", unsafe_allow_html=True)
            
            # Explication du niveau de risque
            st.write("### Risk Level of the Region:")
            st.markdown(f"""
            📅 **Selected Year**: <span style='color: #ffa500; font-weight: bold;'>{selected_year}</span>
            <br><br>
            **This is the risk level for the selected region:** <span style='color: #ffcc00; font-weight: bold;'>{'Unknown' if nearest_data['risk'] == 0 else risk_text}</span>
            <br><br>
            **Number of extreme wind days per year in the selected region**: <span style='color: #ffa500; font-weight: bold;'>{nearest_data['days']}</span>
            """, unsafe_allow_html=True)
            
            # Afficher le graphique temporel
            st.write("### Risk Evolution:")
            time_series_fig = create_time_series(wind_data, nearest_data['lat'], nearest_data['lon'], 'risk')
            if time_series_fig is not None:
                st.plotly_chart(time_series_fig, use_container_width=True)
                
                # Ajouter la légende des niveaux de risque sous le graphique temporel
                st.markdown("""
                <div style="display: flex; justify-content: center; gap: 10px;">
                    <div class="risk-badge risk-low" style="padding: 10px; border-radius: 5px; background: #28a745; color: white;">Low Risk (1)</div>
                    <div class="risk-badge risk-medium" style="padding: 10px; border-radius: 5px; background: #ffc107; color: black;">Medium Risk (2)</div>
                    <div class="risk-badge risk-high" style="padding: 10px; border-radius: 5px; background: #dc3545; color: white;">High Risk (3)</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Créer la carte avec des marqueurs colorés selon le niveau de risque
            m = folium.Map(location=[city_lat, city_lon], zoom_start=5)
            
            # Marker pour la ville recherchée
            folium.Marker(
                location=[city_lat, city_lon],
                popup=f"City: {city_name}, {country_name}",
                icon=folium.Icon(color='orange')
            ).add_to(m)
            
            # Afficher la carte Folium
            st_folium(m, width=725)
        else:
            st.error("Sorry, coordinates for this city could not be found.")
    else:
        st.warning("Please enter both a country and a city.")
