#!/bin/bash

pip install --user cdsapi

# Exécuter le code Python
python3 <<EOF
import cdsapi

dataset = "sis-ecde-climate-indicators"
request = {
    "origin": "reanalysis",
    "temporal_aggregation": ["yearly"],
    "spatial_aggregation": "gridded",
    "variable": [
        "heatwave_days",
        "frost_days",
        "frequency_of_extreme_precipitation",
        "duration_of_meteorological_droughts",
        "days_with_high_fire_danger",
        "extreme_wind_speed_days",
    ]
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
EOF

# Décompresser le fichier .zip téléchargé 
zip_file=$(ls *.zip 2>/dev/null)
output_dir="./donnees_risk_climatique_telechargees"  # Dossier de destination local

# Créer le dossier de destination si nécessaire
mkdir -p "$output_dir"

# Décompresser dans le dossier de destination
if [ -n "$zip_file" ]; then
    echo "Décompression du fichier $zip_file dans le dossier $output_dir..."
    unzip -o "$zip_file" -d "$output_dir"
    echo "Décompression terminée. Les fichiers extraits sont dans le dossier '$output_dir'."
else
    echo "Aucun fichier .zip trouvé pour la décompression."
fi
