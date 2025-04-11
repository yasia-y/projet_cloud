import streamlit as st
import pandas as pd
from fetch_api import get_data_for_plant
from graphs import plot_temperature_humidity

st.set_page_config(page_title="Dashboard Capteurs", layout="wide")
st.title("🌿 Dashboard - Ferme Urbaine Verticale")

plant_id = st.selectbox("Sélectionnez une plante 🌱", [str(i) for i in range(1, 9)])

data = get_data_for_plant(plant_id)

def detect_anomaly(row):
    anomalies = []
    if row["temperature"] > 30:
        anomalies.append("🌡️ Température élevée")
    if row["humidity"] < 40:
        anomalies.append("💧 Humidité faible")
    return anomalies

if data and "results" in data:
    df = pd.DataFrame(data["results"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["anomalies"] = df.apply(detect_anomaly, axis=1)

    st.subheader("📊 Données brutes")
    st.dataframe(df)

    st.subheader("📈 Graphe Température & Humidité")
    plot_temperature_humidity(df)

    st.subheader("🚨 Anomalies détectées")
    anomalies_df = df[df["anomalies"].apply(len) > 0]
    if not anomalies_df.empty:
        for _, row in anomalies_df.iterrows():
            st.error(f"[{row['timestamp']}] - {', '.join(row['anomalies'])}")
    else:
        st.success("✅ Aucune anomalie détectée récemment !")
else:
    st.warning("Aucune donnée disponible pour cette plante.")

