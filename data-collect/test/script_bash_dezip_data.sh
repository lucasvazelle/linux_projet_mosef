# Décompresser le fichier .zip téléchargé (quel que soit le nom)
zip_file=$(ls *.zip 2>/dev/null)
output_dir="../webapp"  # Dossier de destination local

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
