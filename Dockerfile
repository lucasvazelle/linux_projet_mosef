FROM ubuntu:20.04

# Mettre à jour le système et installer les dépendances
RUN apt update && apt-get install -y curl && apt-get install -y python3 && apt-get install -y python3-pip

WORKDIR /webapp_climatique/app


COPY . .

RUN chmod +x *.sh

RUN python3 -m pip install -r requirements.txt

CMD ["bash", "start_app.sh"]
