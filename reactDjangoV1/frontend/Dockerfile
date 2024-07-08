# Étape 1: Définir l'image de base
FROM node:14-alpine

# Étape 2: Définir le répertoire de travail
WORKDIR /app

# Étape 3: Copier les fichiers de dépendances
COPY package.json package-lock.json ./

# Étape 4: Installer les dépendances
RUN npm install
RUN npm install @stripe/stripe-js

# Étape 5: Copier le reste des fichiers du projet dans le conteneur
COPY . .

# Étape 6: Exposer le port 3000 pour permettre l'accès externe
EXPOSE 3000

# Étape 7: Lancer l'application via npm start
CMD ["npm", "start"]
