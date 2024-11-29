FROM ubuntu:20.04

RUN apt update && apt-get install -y curl && apt-get install -y python3 && apt-get install -y python3-pip

RUN python3 -m pip install --upgrade pip

WORKDIR /home/webapp/webapp_climatique

COPY . .

RUN bash ./installation_archive_log.sh

RUN chmod +x *.sh

RUN python3 -m pip install -r requirements.txt

CMD ["bash", "start_app.sh"]