 #!/bin/bash
echo "Getting data from API: opendata.paris.fr"
OUTPUT_PATH=$1
curl -s -X 'GET' "https://opendata.paris.fr/api/v2/catalog/datasets/casvp-immobilisations-etat-des-amortissement/exports/csv"
$OUTPUT_PATH
