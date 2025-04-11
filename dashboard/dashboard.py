# This is the main entry point for the Streamlit dashboard.
# It should define the layout, controls, and logic to display real-time or historical sensor data.
import streamlit as st
import pandas as pd
import requests
import psycopg2

# Configuration de la base de données
DB_HOST = "localhost"  # Utilisez "db" si le dashboard est dans le même réseau Docker
DB_PORT = 5432
DB_NAME = "ferme"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

st.set_page_config(page_title="Dashboard Capteurs", layout="wide")
st.title("🧪 Dashboard - Données Capteurs (API Flask)")


@st.cache_data(ttl=10)  # Fixe l'intervalle de rafraîchissement à 10 secondes
# Fonction pour récupérer les données depuis PostgreSQL
def load_data_from_db():
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        query = "SELECT * FROM sensor_data;"  # Remplacez par votre requête
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return pd.DataFrame()


def load_data():
    return load_data_from_db()


# Affichage des données
st.subheader("📊 Données reçues")
data_placeholder = st.empty()

# Rafraîchissement manuel uniquement
if st.sidebar.button("Rafraîchir maintenant"):
    df = load_data()
    if not df.empty:
        st.dataframe(df)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            for sensor_type in df["type_donnee"].unique():
                sensor_data = df[df["type_donnee"] == sensor_type]
                st.line_chart(sensor_data.set_index("timestamp")["valeur"])
    else:
        st.warning("Aucune donnée disponible.")
