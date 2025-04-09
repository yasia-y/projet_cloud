# This is the main entry point for the Streamlit dashboard.
# It should define the layout, controls, and logic to display real-time or historical sensor data.
import streamlit as st
import pandas as pd
import requests
import time

API_URL = "http://localhost:8000/api/orders"

st.set_page_config("Dashboard Capteurs", layout="wide")
st.title("🧪 Dashboard - Données Capteurs (API Flask)")

# Rafraîchissement automatique
auto = st.sidebar.checkbox("Rafraîchissement automatique", True)
delay = st.sidebar.slider("Intervalle (sec)", 2, 30, 5)

placeholder = st.empty()


def load_data():
    r = requests.get(API_URL)
    data = r.json()
    df = pd.DataFrame(data)
    return df


while True:
    with placeholder.container():
        df = load_data()
        st.subheader("📊 Données reçues")
        st.dataframe(df)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            for capteur in df["item"].unique():
                capteur_df = df[df["item"] == capteur]
                st.line_chart(capteur_df.set_index("timestamp")["quantity"])

    if not auto:
        break
    time.sleep(delay)
