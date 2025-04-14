# Projet Cloud - Supervision de Ferme Urbaine

Ce projet est une application de supervision pour une ferme urbaine connectée.  
Il permet de collecter, analyser et visualiser les données des capteurs (température, humidité) installés sur différentes plantes.  
L'application est composée de plusieurs services conteneurisés, orchestrés avec Docker Compose.

## Fonctionnalités principales

### Ingestion des données des capteurs

- Les capteurs envoient des données (température, humidité, etc.) à une API d'ingestion.
- Les données sont validées, transformées et stockées dans une base de données PostgreSQL.

### Détection d'anomalies

- Analyse des données pour détecter des anomalies environnementales (température ou humidité hors des seuils).
- Détection des écarts entre capteurs pour une même plante.

### Dashboard interactif

- Visualisation des données en temps réel via des graphiques.
- Affichage des anomalies détectées.
- Comparaison des données entre plusieurs capteurs.

### Simulation de capteurs

- Génération de données simulées pour tester l'application.

## Architecture des services

Le projet est composé des services suivants :

### 1. API d'ingestion (`ingestion-api`)

- **Langage** : Python (FastAPI)  
- **Port exposé** : 8000  
- **Rôle** :
  - Recevoir les données des capteurs.
  - Valider et transformer les données.
  - Insérer les données dans la base PostgreSQL.
  - Détecter des anomalies simples.
- **Fichier(s)** :
  - `main.py` : Contient les endpoints de l'API.
  - `validator.py` : Valide les données des capteurs.
  - `parser.py` : Décode les données encodées en MsgPack/Base64.

### 2. Base de données (`database`)

- **Technologie** : PostgreSQL  
- **Port exposé** : 5432  
- **Rôle** :
  - Stocker les données des capteurs.
  - Fournir des données pour le dashboard et les analyses.
- **Fichier(s)** :
  - `init.sql` : Script SQL pour créer les tables nécessaires.

### 3. Détection d'anomalies (`detection`)

- **Langage** : Python  
- **Rôle** :
  - Analyser les données pour détecter des anomalies environnementales.
  - Identifier les écarts entre capteurs pour une même plante.
- **Fichier(s)** :
  - `detector.py` : Contient la logique de détection des anomalies.

### 4. Simulation de capteurs (`sensor`)

- **Langage** : Python  
- **Rôle** :
  - Générer des données simulées (température, humidité).
  - Envoyer les données à l'API d'ingestion.
- **Fichier(s)** :
  - `sensor.py` : Génère et envoie les données simulées.

### 5. Dashboard (`dashboard`)

- **Langage** : Python (Streamlit)  
- **Port exposé** : 8502  
- **Rôle** :
  - Visualiser les données des capteurs.
  - Afficher les anomalies détectées.
  - Comparer les données entre plusieurs capteurs.
- **Fichier(s)** :
  - `dashboard.py` : Interface utilisateur principale.
  - `fetch_api.py` : Récupère les données depuis l'API d'ingestion.
  - `graphs.py` : Génère les graphiques.


---

## Structure du projet

```
projet_cloud/
├── dashboard/               # Interface utilisateur (Streamlit)
│   ├── dashboard.py         # Interface principale
│   ├── fetch_api.py         # Requête à l’API d’ingestion
│   ├── graphs.py            # Génération des graphiques
│   ├── requirements.txt     # Dépendances Python
│   └── Dockerfile           # Image Docker
│
├── detection/               # Détection d’anomalies
│   ├── detector.py          # Analyse des données
│   ├── utils.py             # Fonctions utilitaires
│   ├── requirements.txt     # Dépendances Python
│   └── Dockerfile           # Image Docker
│
├── ingestion-api/           # API REST (FastAPI)
│   ├── main.py              # Endpoints de l’API
│   ├── validator.py         # Validation des données
│   ├── parser.py            # Décodage des données
│   ├── requirements.txt     # Dépendances Python
│   └── Dockerfile           # Image Docker
│
├── sensor/                  # Simulateur de capteurs
│   ├── sensor.py            # Génération de données aléatoires
│   └── Dockerfile           # Image Docker
│
├── database/                # Base de données PostgreSQL
│   ├── init.sql             # Script d’initialisation
│   └── Dockerfile           # Image Docker
│
├── docker-compose.yaml      # Orchestration des services
├── README.md                # Documentation du projet
└── LICENSE                  # Licence (MIT)

```

## Prérequis

- [Docker](https://www.docker.com/) et [Docker Compose](https://docs.docker.com/compose/) installés sur votre machine.
- Python 3.12 (facultatif, pour exécuter les services localement sans conteneur).

---

## Installation & exécution

### 1. Cloner le projet

```bash
git clone https://github.com/yasia-y/projet_cloud.git
cd projet_cloud
```
### 2. Lancer les services avec Docker Compose

```bash
docker-compose up --build
```
Une fois les services démarrés, vous pourrez accéder aux dashboard sur http://localhost:8502


