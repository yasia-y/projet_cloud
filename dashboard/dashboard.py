import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from fetch_api import get_plants, get_sensors, get_sensor_data
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Supervision Ferme Urbaine", 
    layout="wide",
    page_icon="🌿"
)

# Style CSS
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
        # Auto-refresh toutes les 15 secondes
        auto_refresh = st.sidebar.checkbox(
            "🔄 Actualisation automatique (15s)", 
            key="auto_refresh_key",
            value=True
        )
        if auto_refresh:
            st_autorefresh(interval=15_000, key="data_refresher")

        with st.sidebar:
            st.header("Filtres")
            
            if st.button("🔄 Actualiser maintenant", key="manual_refresh"):
                st.experimental_rerun()

            # Sélection des plantes
            try:
                plants = get_plants()
                selected_plant = st.selectbox(
                    "Plante 🌱", 
                    options=plants,
                    format_func=lambda x: f"PLANTE {x}",
                    key="plant_selector"
                )

                # Sélection des capteurs
                sensors = get_sensors(selected_plant)
                selected_sensor = st.selectbox(
                    "Capteur 📡", 
                    options=sensors,
                    format_func=lambda x: f"{x['sensor_id']} ({x['sensor_version']})",
                    key="sensor_selector"
                )

                # Sélection de la période
                time_range = st.selectbox(
                    "Période 📅",
                    options=["1h", "24h", "7j"],
                    index=1,
                    key="time_selector"
                )

            except Exception as e:
                st.error(f"Erreur de connexion : {str(e)}")
                st.stop()

        # Calcul des dates
        time_map = {"1h": 1, "24h": 24, "7j": 168}
        end_time = datetime.utcnow().replace(second=0, microsecond=0)
        start_time = end_time - timedelta(hours=time_map[time_range])

        # Récupération des données principales
        try:
            main_data = get_sensor_data(
                plant_id=selected_plant,
                sensor_id=selected_sensor["sensor_id"],
                start=start_time,
                end=end_time
            )
            df = pd.DataFrame(main_data)
        except Exception as e:
            st.error(f"Erreur données : {str(e)}")
            st.stop()

        # Traitement des données
        df['anomaly'] = df.get('anomaly', False)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        latest = df.iloc[-1].to_dict() if not df.empty else {}

        # Section métriques
        col1, col2, col3, col4 = st.columns(4)
        is_anomaly = latest.get('anomaly', False)
        
        with col1:
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
            anomaly_count = df['anomaly'].sum()
            st.markdown(f'<div class="metric-card {"warning" if anomaly_count > 0 else ""}">'
                        f'<h3>🚨 Anomalies</h3>'
                        f'<h1>{int(anomaly_count)}</h1></div>', 
                        unsafe_allow_html=True)
        
        with col4:
            st.markdown(f'<div class="metric-card">'
                        f'<h3>📟 Version Capteur</h3>'
                        f'<h1>{selected_sensor.get("sensor_version", "N/A")}</h1></div>', 
                        unsafe_allow_html=True)

        # Visualisation principale
        if not df.empty:
            fig = px.line(df, x="timestamp", y=["temperature", "humidity"],
                        title=f"Mesures pour Plante {selected_plant} - Capteur {selected_sensor['sensor_id']}",
                        height=500)
            st.plotly_chart(fig, use_container_width=True)

      
        if anomaly_count > 0:
            st.subheader("🚨 Détail des Anomalies")
            anomalies_df = df[df["anomaly"]].sort_values("timestamp", ascending=False)
        
            for _, row in anomalies_df.iterrows():
                cols = st.columns([2, 6, 2])
                with cols[0]:
                    st.markdown(f"**{row['timestamp'].strftime('%d/%m %H:%M')}**")
                with cols[1]:
                    issues = []
                    temp = row.get('temperature', 0)
                    hum = row.get('humidity', 0)
                    
                    if temp > 35:
                        issues.append(f"Température critique ({temp:.1f}°C)")
                    elif temp < 10:
                        issues.append(f"Température basse ({temp:.1f}°C)")
                        
                    if hum > 85:
                        issues.append(f"Humidité élevée ({hum:.1f}%)")
                    elif hum < 25:
                        issues.append(f"Humidité basse ({hum:.1f}%)")
                        
                    if row.get('cross_sensor_issue', False):
                        issues.append("Écart inter-capteurs")
                        
                    st.write(", ".join(issues) if issues else "Anomalie non spécifiée")
                with cols[2]:
                    st.button("📋 Détails", key=f"details_{row['timestamp']}")

        # Comparaison inter-capteurs
        if len(sensors) > 1:
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
                fig = px.line(comparison_df, 
                            x="timestamp", 
                            y="temperature",
                            color="sensor_id",
                            title=f"Comparaison des températures - Plante {selected_plant}",
                            height=400)
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur critique : {str(e)}")
        st.stop()

if __name__ == "__main__":
    main()
