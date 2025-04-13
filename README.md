# 🌱 Projet Cloud – Supervision de ferme urbaine

Ce projet est une application cloud de supervision dédiée à une ferme urbaine connectée.  
Elle permet de collecter, analyser et visualiser les données environnementales transmises par des capteurs (température, humidité) installés sur différentes plantations.

---

## Objectif du projet

L’objectif est de développer et simuler le déploiement d’une architecture cloud capable de :

1. Recevoir en temps réel les données des capteurs de la ferme urbaine simulée.
2. Stocker l’historique de ces données afin de les rendre exploitables pour le suivi et l’analyse.
3. Permettre à un opérateur de superviser les données de chaque capteur via une interface simplifiée.
4. Détecter automatiquement les anomalies (capteur défectueux ou problème sur la culture) pour notifier rapidement l’opérateur.

---

## Fonctionnalités principales

- **Ingestion de données capteurs**  
  Validation, traitement et stockage des informations dans une base de données PostgreSQL.

- **Détection d’anomalies**  
  Analyse des données pour identifier les événements anormaux via un module d’alerte automatique.

- **Dashboard interactif**  
  Visualisation en temps réel des mesures et des anomalies grâce à une interface utilisateur simple réalisée avec Streamlit.

- **Simulation de capteurs**  
  Génération et envoi de données simulées pour tester le système sans matériel réel.

---

## Structure du projet

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


## Prérequis

- [Docker](https://www.docker.com/) et [Docker Compose](https://docs.docker.com/compose/) installés sur votre machine.
- Python 3.12 (facultatif, pour exécuter les services localement sans conteneur).

---

## ⚙️ Installation & Exécution

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


