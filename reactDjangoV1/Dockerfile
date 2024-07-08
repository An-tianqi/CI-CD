FROM python:3.9-slim-buster


# Dossier pour le travail
# dépendances
WORKDIR /reactDjangoApp
COPY . .

RUN pip install -r requirements.txt

# Installer Firefox et Xvfb
#RUN apt-get update && apt-get install -y --no-install-recommends firefox-esr xvfb
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     firefox-esr \
#     xvfb \
# && rm -rf /var/lib/apt/lists/*
# Installation de Google Chrome et ChromeDriver
RUN apt-get update && apt-get install -y --no-install-recommends firefox-esr xvfb

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

