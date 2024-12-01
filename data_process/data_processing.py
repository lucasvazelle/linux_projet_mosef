import xarray as xr
import pandas as pd
import numpy as np
import os

# Déterminer le répertoire du script pour générer les chemins relatifs
script_dir = os.path.dirname(os.path.abspath(__file__))

# Créer les chemins relatifs pour les fichiers NetCDF
wind_file_path = os.path.join(script_dir, "24_extreme_wind_speed_days-projections-yearly-rcp_4_5-wrf381p-ipsl_cm5a_mr-r1i1p1-grid-v1.0.nc")
precipitation_file_path = os.path.join(script_dir, "15_frequency_of_extreme_precipitation-projections-yearly-rcp_4_5-wrf381p-ipsl_cm5a_mr-r1i1p1-grid-v1.0.nc")

# Charger les datasets avec xarray
print("🔄 Chargement des datasets...")
wind = xr.open_dataset(wind_file_path, engine="netcdf4")
precipitation = xr.open_dataset(precipitation_file_path, engine="netcdf4")
print("✅ Datasets chargés avec succès.")

# Convertir les datasets xarray en DataFrame pandas
print("⚙️ Conversion des datasets en DataFrame pandas...")
wind_df = wind.to_dataframe().reset_index()
precipitation_df = precipitation.to_dataframe().reset_index()
print("✅ Conversion réussie.")

# Traitement du dataset wind
print("⚙️ Traitement du dataset wind...")
wind_df = wind_df.drop('height', axis=1)  # Suppression de la colonne 'height'
wind_df['year'] = wind_df['time'].dt.year  # Extraction de l'année
wind_df = wind_df[(wind_df['year'] >= 2025) & (wind_df['year'] <= 2035)]  # Filtrage des années 2025-2035

# Calcul des jours et des percentiles pour wind
wind_df['days'] = wind_df['data'].dt.days
percentiles_wind = wind_df['days'].quantile([0.33, 0.66])
print(f"📊 Percentiles calculés pour wind : 33% = {percentiles_wind[0.33]}, 66% = {percentiles_wind[0.66]}")

# Fonction unique pour assigner le risque
def assign_risk(value, percentiles):
    if pd.isna(value):
        return 'Missing Data'  # Gestion des données manquantes
    elif value <= percentiles[0.33]:
        return 'Low'  # Risque faible
    elif value <= percentiles[0.66]:
        return 'Medium'  # Risque modéré
    else:
        return 'High'  # Risque élevé

# Application de la fonction sur les jours dans le dataset wind
wind_df['risk'] = wind_df['days'].apply(lambda x: assign_risk(x, percentiles_wind))
print("✅ Risque assigné au dataset wind.")

# Sauvegarde du dataset wind en CSV
wind_df.to_csv("../application/wind.csv", index=False)
print("💾 Dataset wind sauvegardé sous 'wind.csv'.")

# Traitement du dataset precipitation
print("⚙️ Traitement du dataset precipitation...")
precipitation_df['year'] = precipitation_df['time'].dt.year  # Extraction de l'année
precipitation_df = precipitation_df[(precipitation_df['year'] >= 2025) & (precipitation_df['year'] <= 2035)]  # Filtrage des années 2025-2035

# Calcul des percentiles pour les précipitations
precipitation_df['days'] = precipitation_df['data'].dt.days
percentiles_precip = precipitation_df['days'].quantile([0.33, 0.66])
print(f"📊 Percentiles calculés pour precipitation : 33% = {percentiles_precip[0.33]}, 66% = {percentiles_precip[0.66]}")

# Application de la fonction sur les jours dans le dataset precipitation
precipitation_df['risk'] = precipitation_df['days'].apply(lambda x: assign_risk(x, percentiles_precip))
print("✅ Risque assigné au dataset precipitation.")

# Sauvegarde du dataset precipitation en CSV
precipitation_df.to_csv("../application/precipitation.csv", index=False)
print("💾 Dataset precipitation sauvegardé sous 'precipitation.csv'.")

print("🎉 Script terminé avec succès.")
