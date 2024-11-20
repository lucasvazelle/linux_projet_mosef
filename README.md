# linux_projet_mosef

[commander à lancer] cf branch master pour l'évalusation Feat 1: Un commentaire précisant le retour attendu Feat 2: Un exemple de retour
Cette application web permet d'afficher de manière graphique et intéractive des cartes européennes d'indicateur de risque climatique calculées par Copernicus sur plusieurs années. 
Vous pouvez renseigner des coorodonnées géographique pour connaître le niveau de risque climatique associée à l'année et l'indicateur choisi.
Par exemple, la première page affiche le nombre de jours froid "extrême".

2 possibilitées

1ère possibilité, lancer:
$pip3 install -r requirements.txt 
$streamlit run webapp/webapp.py

2èeme possibilité, lancer (pré requis : avoir le logiciel docker) : 
docker pull  lucasvazelle/mywebapp
docker run -p 8501:8501 lucasvazelle/mywebapp

