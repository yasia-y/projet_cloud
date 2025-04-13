**Objectif du projet**

Ce projet a pour objectif de concevoir, développer et simuler le déploiement d'une architecture cloud dédiée à la supervision d'une ferme urbaine connectée. L’architecture mise en place vise à offrir une solution complète et évolutive répondant aux besoins suivants :

- Réception en temps réel des données capteurs
  Les capteurs répartis dans la ferme (température, humidité, etc.) transmettent régulièrement leurs mesures. Ces données sont collectées automatiquement via une API d’ingestion et transmises en temps réel aux services backend.

- Stockage des données historiques
  L’ensemble des données reçues est validé, puis stocké de manière sécurisée dans une base de données PostgreSQL. Ce stockage permet d’effectuer des analyses historiques, des audits, ou encore des comparaisons temporelles.

- Interface de supervision intuitive
  Un dashboard interactif (via Streamlit) permet à un opérateur de la ferme de visualiser simplement les données remontées par les capteurs. Ce tableau de bord rend possible la navigation entre les différentes plantes, ainsi que la consultation de l’évolution des conditions environnementales.

- Détection proactive des anomalies
  Un service de détection autonome analyse les données collectées pour repérer tout comportement inhabituel (données incohérentes ou alarmantes). Ces anomalies peuvent signaler : un problème potentiel sur une plante (manque  ou surplus d’humidité, manque ou excès de chaleur). En cas de détection, une alerte est remontée automatiquement sur le dashboard, permettant à l’opérateur d’agir rapidement.

**Prérequis**

- Docker et Docker Compose installés sur votre machine.
- Python 3.12 (optionnel, pour exécuter localement sans Docker

**Installation & exécution**

1. Cloner le dépôt
git clone https://github.com/yasia-y/projet_cloud.git
cd projet_cloud

3. Lancer les services avec Docker Compose
docker-compose up --build

4. Accéder au dashboard
 http://localhost:8502
