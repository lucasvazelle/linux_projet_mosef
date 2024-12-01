# linux_projet_mosef

# Visualisation des indicateurs de risque climatique 🌍  

## Introduction  
Ce projet a été développé dans le cadre d'une évaluation pour le Master MoSEF en Data Science de Paris 1 Panthéon-Sorbonne. Il consiste à créer une application web interactive permettant d'appréhender certains risques climatiques en Europe pour les prochaines années, en utilisant des indicateurs calculées par **Copernicus**.  

Avec cette application, les utilisateurs peuvent entrer des coordonnées géographiques pour afficher le niveau de risque climatique associé à une année et à un indicateur spécifique. 
Il est aussi affiché un graphique de l'évolution de la prévision du risque selon les années pour la localisation donnée, ainsi que d'une carte de permettant de visualiser l'adresse saisie. 

## Fonctionnalités  
- Recherche de risques climatiques à l'aide d'une adresse.  
- Possibilité de sélectionner deux indicateurs de risque climatique. 
- Visualisation interactive.  


 
### 1. Lancer l'application en local 💻

Tout d'abord, clonez le dépôt et activez votre environnement virtuel. 
 
Vous pouvez exécuter l'application localement en utilisant les commandes suivantes :  

```
bash start_app.sh

```

### 2. Lancer avec Docker (recommandé) 🐳
Vous pouvez également déployer l'application via Docker. Assurez-vous d'avoir installé Docker au préalable.
```
docker pull lucasvazelle/webapp_climatique_groupe_quatre_mosef
docker run -p 5004:5004 lucasvazelle/webapp_climatique_groupe_quatre_mosef
```
Cliquez sur Local, Internal ou External URL selon votre contexte d'excécution
