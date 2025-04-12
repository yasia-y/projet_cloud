import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from fetch_api import get_plants, get_sensors, get_sensor_data

st.set_page_config(
    page_title="Supervision Ferme Urbaine", 
    layout="wide",
    page_icon="🌿"
)

# Configuration du style
st.markdown("""
<style>
    .metric-card {
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    .critical { background-color: #ffcccc !important; }
    .warning { background-color: #fff3cd !important; }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🌍 Supervision Ferme Urbaine Verticale - Atos x LIRIS")
    
    try:
        # Sidebar pour les filtres
        with st.sidebar:
            st.header("Filtres")
            
            # Récupération des plantes avec gestion d'erreur
            try:
                plants = get_plants()
                if not plants:
                    st.error("Aucune plante disponible dans la base de données")
                    st.stop()
            except Exception as e:
                st.error(f"Erreur de connexion à l'API : {str(e)}")
                st.stop()

            selected_plant = st.selectbox(
                "Plante 🌱", 
                options=plants,
                format_func=lambda x: f"PLANTE {x}"
            )
            
            # Récupération des capteurs avec gestion d'erreur
            try:
                sensors = get_sensors(selected_plant)
                if not sensors:
                    st.error("Aucun capteur disponible pour cette plante")
                    st.stop()
            except Exception as e:
                st.error(f"Erreur de récupération des capteurs : {str(e)}")
                st.stop()

            selected_sensor = st.selectbox(
                "Capteur 📡", 
                options=sensors,
                format_func=lambda x: f"{x['sensor_id']} ({x['sensor_version']})"
            )
            
            time_range = st.selectbox(
                "Période 📅",
                options=["1h", "24h", "7j"],
                index=1
            )

        # Calcul des dates
        time_map = {"1h": 1, "24h": 24, "7j": 168}
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_map[time_range])

        # Récupération des données avec gestion d'erreur
        try:
            data = get_sensor_data(
                plant_id=selected_plant,
                sensor_id=selected_sensor["sensor_id"],
                start=start_time,
                end=end_time
            )
        except Exception as e:
            st.error(f"Erreur de récupération des données : {str(e)}")
            st.stop()

        if not data:
            st.warning("Aucune donnée disponible pour cette configuration")
            return

        df = pd.DataFrame(data)
        
        # Vérification du format des données
        if 'anomaly' not in df.columns:
            df['anomaly'] = False
            
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Gestion spécifique de la dernière mesure
        latest = df.iloc[-1].copy()
        if isinstance(latest, pd.Series):
            latest = latest.to_dict()

        # Section des métriques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            is_anomaly = latest.get('anomaly', False)
            if isinstance(is_anomaly, pd.Series):
                is_anomaly = is_anomaly.any()
            st.markdown(f'<div class="metric-card {"critical" if is_anomaly else ""}">'
                        f'<h3>🌡 Température Actuelle</h3>'
                        f'<h1>{latest.get("temperature", 0.0):.1f}°C</h1></div>', 
                        unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'<div class="metric-card {"critical" if is_anomaly else ""}">'
                        f'<h3>💧 Humidité Actuelle</h3>'
                        f'<h1>{latest.get("humidity", 0.0):.1f}%</h1></div>', 
                        unsafe_allow_html=True)
        
        with col3:
            anomaly_count = df['anomaly'].sum() if 'anomaly' in df.columns else 0
            st.markdown(f'<div class="metric-card {"warning" if anomaly_count > 0 else ""}">'
                        f'<h3>🚨 Anomalies</h3>'
                        f'<h1>{int(anomaly_count)}</h1></div>', 
                        unsafe_allow_html=True)
        
        with col4:
            sensor_version = selected_sensor.get("sensor_version", "N/A")
            st.markdown(f'<div class="metric-card">'
                        f'<h3>📟 Version Capteur</h3>'
                        f'<h1>{sensor_version}</h1></div>', 
                        unsafe_allow_html=True)

        # Visualisations
        st.subheader("📈 Historique des Mesures")
        if not df.empty:
            fig = px.line(df, x="timestamp", y=["temperature", "humidity"],
                        labels={"value": "Valeur", "timestamp": "Heure"},
                        title=f"Mesures pour Plante {selected_plant} - Capteur {selected_sensor['sensor_id']}",
                        height=500)
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

        # Détails des anomalies
        if anomaly_count > 0:
            st.subheader("🚨 Détail des Anomalies")
            anomalies_df = df[df["anomaly"]].sort_values("timestamp", ascending=False)
            
            for _, row in anomalies_df.iterrows():
                cols = st.columns([2, 6, 2])
                with cols[0]:
                    st.markdown(f"**{row['timestamp'].strftime('%d/%m %H:%M')}**")
                with cols[1]:
                    issues = []
                    if row['temperature'] > 35:
                        issues.append(f"Température critique ({row['temperature']}°C)")
                    if row['temperature'] < 10:
                        issues.append(f"Température basse ({row['temperature']}°C)")
                    if row['humidity'] > 85:
                        issues.append(f"Humidité élevée ({row['humidity']}%)")
                    if row['humidity'] < 25:
                        issues.append(f"Humidité basse ({row['humidity']}%)")
                    if row.get('cross_sensor_issue'):
                        issues.append("Écart inter-capteurs")
                    st.write(", ".join(issues))
                with cols[2]:
                    st.button("📋 Détails", key=row["timestamp"])

        # Comparaison inter-capteurs
        if len(sensors) > 1 and not df.empty:
            st.subheader("🔍 Comparaison Inter-Capteurs")
            all_data = []
            for sensor in sensors:
                try:
                    sensor_data = get_sensor_data(
                        plant_id=selected_plant,
                        sensor_id=sensor["sensor_id"],
                        start=start_time,
                        end=end_time
                    )
                    if sensor_data:
                        df_sensor = pd.DataFrame(sensor_data)
                        df_sensor["sensor_id"] = sensor["sensor_id"]
                        all_data.append(df_sensor)
                except Exception:
                    continue
            
            if all_data:
                comparison_df = pd.concat(all_data)
                fig = px.line(comparison_df, x="timestamp", y="temperature",
                            color="sensor_id", 
                            title="Comparaison des Températures entre Capteurs",
                            height=400)
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Une erreur critique est survenue : {str(e)}")
        st.stop()

if __name__ == "__main__":
    main()
