# This is the main entry point for the Streamlit dashboard.
# It should define the layout, controls, and logic to display real-time or historical sensor data.
import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000/api/orders"

st.set_page_config(page_title="Dashboard Capteurs", layout="wide")
st.title("🧪 Dashboard - Données Capteurs (API Flask)")


@st.cache_data(ttl=10)  # Fixe l'intervalle de rafraîchissement à 10 secondes
def load_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return pd.DataFrame()


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
