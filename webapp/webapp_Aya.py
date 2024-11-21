import streamlit as st
import pydeck as pdk
import xarray as xr
import os
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from datetime import datetime
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title="Climate Indicator",
    page_icon="🌍",
    layout="wide"
)

# CSS personnalisé
# CSS personnalisé
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .risk-indicator {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .title-container {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #ffffff 0%, #f5f7f9 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    /* Ajoutez ici le nouveau style */
    .main .block-container {
        background-color: #f5f5f5;
        padding: 2rem;
        border-radius: 1rem;
    }
</style>
""", unsafe_allow_html=True)

name_mapping = {
    "frost_days": "❄️ Frost Days",
    "frequency_of_extreme_precipitation": "🌧️ Extreme Precipitation",
    "duration_of_meteorological": "🏜️ Droughts",
    "heat_waves": "🌡️ Heat Waves",
    "days_with_high_fire": "🔥 Fire Risk",
    "extreme_wind_speed": "🌪️ Extreme Wind"
}

# Fonction pour extraire le nom simplifié
def clean_filename(filename):
    base_name = filename.split('-')[0]
    cleaned = '_'.join(base_name.split('_')[1:])
    return name_mapping.get(cleaned, cleaned)

@st.cache_data
def load_netcdf_data(nc_file):
    """Charge un fichier NetCDF"""
    try:
        return xr.open_dataset(nc_file, engine="netcdf4")
    except Exception as e:
        st.error(f"Error while loading the file {nc_file}: {str(e)}")
        return None

@st.cache_data
def load_all_netcdf_files(directory):
    """Charge tous les fichiers NetCDF d'un répertoire"""
    datasets = []
    filenames = []
    seen_files = set()
    
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith(".nc"):
                    file_path = os.path.join(root, filename)
                    if file_path not in seen_files:
                        seen_files.add(file_path)
                        dataset = load_netcdf_data(file_path)
                        if dataset is not None:
                            datasets.append(dataset)
                            filenames.append(filename)
        return datasets, filenames
    except Exception as e:
        st.error(f"Error while loading files: {str(e)}")
        return [], []

@st.cache_data(ttl=3600)
def geocode_city(city_name):
    """Géocode une ville en coordonnées lat/lon"""
    try:
        geolocator = Nominatim(user_agent="my_climate_app")
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude, location.address
        return None, None, None
    except GeocoderTimedOut:
        st.error("The geocoding service did not respond in time")
        return None, None, None

def get_value_and_risk(ds, latitude, longitude, year):
    """Calcule la valeur et le niveau de risque"""
    try:
        premiere_variable = list(ds.data_vars)[0]
        valeur = float(ds[premiere_variable].sel(
            lat=latitude, 
            lon=longitude, 
            time=str(year), 
            method="nearest"
        ).values)
        
        all_values = ds[premiere_variable].sel(time=str(year)).values
        valid_values = all_values[~np.isnan(all_values)].flatten()
        
        if len(valid_values) > 0:
            quintiles = np.percentile(valid_values, [20, 40, 60, 80])
            
            if valeur <= quintiles[0]:
                risk_level = 1
            elif valeur <= quintiles[1]:
                risk_level = 2
            elif valeur <= quintiles[2]:
                risk_level = 3
            elif valeur <= quintiles[3]:
                risk_level = 4
            else:
                risk_level = 5
        else:
            risk_level = 0
            
    except Exception as e:
        st.warning(f"Error while calculating the value: {str(e)}")
        valeur = 0
        risk_level = 0
        
    return valeur, risk_level

def get_risk_color(risk_level):
    """Retourne une couleur en fonction du niveau de risque"""
    colors = {
        0: "#808080",  # Gris pour les données manquantes
        1: "#00FF00",  # Vert
        2: "#90EE90",  # Vert clair
        3: "#FFD700",  # Jaune
        4: "#FFA500",  # Orange
        5: "#FF0000"   # Rouge
    }
    return colors.get(risk_level, "#808080")

def create_time_series(ds, lat, lon, variable_name):
    """Crée un graphique temporel des données"""
    try:
        time_series = ds[variable_name].sel(
            lat=lat, 
            lon=lon, 
            method='nearest'
        ).to_dataframe()
        
        fig = px.line(
            time_series,
            y=variable_name,
            title=f"Temporal evolution at {lat:.2f} °N and {lon:.2f}°E",
            labels={"index": "Date", "y": "Valeur"},
        )
        
        fig.update_layout(
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig
    except Exception as e:
        st.error(f"Error while creating the chart:{str(e)}")
        return None

def show_about_widget():
    """Affiche la légende et les informations à propos de l'application"""
    with st.sidebar:
        # Légende des niveaux de risque
        st.markdown("""
            <div style="background-color: white; padding: 10px; border-radius: 5px; margin: 10px 0;">
        <h4>Risk Level Legend</h4>
        <div style="display: flex; margin-bottom: 5px;">
        <div style="width: 20px; height: 20px; background-color: #00FF00; border-radius: 50%; margin-right: 10px;"></div>
        <div>Very Low Risk (1/5)</div>
        </div>
        <div style="display: flex; margin-bottom: 5px;">
        <div style="width: 20px; height: 20px; background-color: #90EE90; border-radius: 50%; margin-right: 10px;"></div>
        <div>Low Risk (2/5)</div>
        </div>
        <div style="display: flex; margin-bottom: 5px;">
        <div style="width: 20px; height: 20px; background-color: #FFD700; border-radius: 50%; margin-right: 10px;"></div>
        <div>Moderate Risk (3/5)</div>
        </div>
        <div style="display: flex; margin-bottom: 5px;">
        <div style="width: 20px; height: 20px; background-color: #FFA500; border-radius: 50%; margin-right: 10px;"></div>
        <div>High Risk (4/5)</div>
        </div>
        <div style="display: flex; margin-bottom: 5px;">
        <div style="width: 20px; height: 20px; background-color: #FF0000; border-radius: 50%; margin-right: 10px;"></div>
        <div>Very High Risk (5/5)</div>
        </div>
        <div style="display: flex; margin-bottom: 5px;">
        <div style="width: 20px; height: 20px; background-color: #808080; border-radius: 50%; margin-right: 10px;"></div>
        <div>Missing Data</div>
        </div>
        </div>

        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        with st.expander("ℹ️ About the application"):
            st.markdown("""
            ### 🌍 Global Vision
            Our predictive climate risk analysis application is primarily aimed at insurance professionals. 
            Anticipate climate risks to optimize your coverage strategies.

    
            ### 📊 Indicators
            Les indicateurs analysés incluent :
            - **Heatwave Days** 
            - **Frost Days** 
            - **Meteorological Drought** 
            - **Fire Risk** 
            - **Extreme Winds**
            
            ### 📈 Data
            - Climate Data: NetCDF files
            - Period: 1940-2023
            - Updates: Regular
            - Source : [Climate Data Store](https://cds.climate.copernicus.eu/datasets)
            
            ### 🛠️ Features
            - Search by city
            - Visualization on interactive map
            - Temporal analysis
            - Risk calculation
            """)

def prepare_map_data(ds, year, intensity=0.4, radius=30, color_scheme="Blues"):
    """Prépare les données pour l'affichage sur la carte"""
    try:
        selected_data = ds.sel(time=str(year))
        df = selected_data.to_dataframe().reset_index()
        weight_column = list(df.select_dtypes(include=[np.number]).columns)[-1]
        
        color_ranges = {
            "Blues": [[240, 249, 255, 50], [189, 215, 231, 100], [107, 174, 214, 150],
                     [49, 130, 189, 200], [8, 81, 156, 220]],
            "Reds": [[255, 245, 240, 50], [254, 224, 210, 100], [252, 146, 114, 150],
                    [222, 45, 38, 200], [165, 15, 21, 220]],
            "Greens": [[247, 252, 245, 50], [229, 245, 224, 100], [199, 233, 192, 150],
                      [161, 217, 155, 200], [49, 163, 84, 220]],
            "Spectral": [[158, 1, 66, 50], [213, 62, 79, 100], [244, 109, 67, 150],
                        [253, 174, 97, 200], [254, 224, 139, 220]]
        }
        
        layer = pdk.Layer(
            "HeatmapLayer",
            data=df,
            get_position=["lon", "lat"],
            get_weight=weight_column,
            radiusPixels=radius,
            opacity=intensity,
            colorRange=color_ranges.get(color_scheme, color_ranges["Blues"]),
        )
        
        view_state = pdk.ViewState(
            latitude=df['lat'].mean(),
            longitude=df['lon'].mean(),
            zoom=3,
            pitch=0,
        )
        
        return pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/light-v9'
        )
        
    except Exception as e:
        st.error(f"Error while preparing map data: {str(e)}")
        return None

def main():
    # En-tête
    st.markdown("""
        <div class="title-container">
            <h1 style='text-align: center;'>🌡️ Climate Indicators Analysis</h1>
            <p style='text-align: center;'>Explore and analyze climate data from around the world. </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Parameter")
        show_about_widget()
    
    # Interface de recherche
    # Interface de recherche
    search_col1, search_col2 = st.columns([3, 1])  

    with search_col1:
        city_input = st.text_input(
        "🔍 Search for a city",
        placeholder="Enter the name of a city...",
        label_visibility="collapsed"  # Cache le label
    )
    
    with search_col2:
        if st.button("📍 Locate", use_container_width=True):
            with st.spinner("Searching..."):
                lat, lon, address = geocode_city(city_input)
                if lat and lon:
                    st.session_state['Latitude'] = lat
                    st.session_state['Longitude'] = lon
                    st.success(f"📍 {address}")
                else:
                    st.error("City not found !")
    
    # Coordonnées et année
    coord_col1, coord_col2, coord_col3 = st.columns([1, 1, 2])
    
    with coord_col1:
        latitude = st.number_input(
            "Latitude",
            value=st.session_state.get('latitude', 48.8566),
            format="%.4f"
        )
    
    with coord_col2:
        longitude = st.number_input(
            "Longitude",
            value=st.session_state.get('longitude', 2.3522),
            format="%.4f"
        )
    
    with coord_col3:
        year = st.slider(
            "📅 Year",
            min_value=1979,
            max_value=2023,
            value=2021,
            format="%d"
        )
    
    try:
        with st.spinner("Loading data..."):
            all_datasets, all_filenames = load_all_netcdf_files("./")
            
        if not all_datasets:
            st.error("No data file found")
            return
            
        # Création des onglets avec noms simplifiés
        tab_titles = [clean_filename(filename) for filename in all_filenames]
        tabs = st.tabs(tab_titles)
        
        # Affichage des données
        for i, (ds, filename) in enumerate(zip(all_datasets, all_filenames)):
            with tabs[i]:
                # Calcul des métriques
                valeur, risk_level = get_value_and_risk(ds, latitude, longitude, year)
                
                # Affichage des métriques
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Year", year)

                with col2:
                    st.metric("Value", f"{valeur:.2f}")

                with col3:
                    st.markdown("<br>", unsafe_allow_html=True) 
                    st.markdown(f"""
                        <div style='
                            background-color: {get_risk_color(risk_level)};
                            padding: 10px;
                            border-radius: 5px;
                            text-align: center;
                            color: white;
                        '>
                           Risk level: {risk_level}/5
                        </div>
                    """, unsafe_allow_html=True)
                
                # Carte
                map_data = prepare_map_data(ds, year)
                if map_data:
                    st.pydeck_chart(map_data)
                
                # Graphique temporel
                variable_name = list(ds.data_vars)[0]
                fig = create_time_series(ds, latitude, longitude, variable_name)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.error(f"UAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()