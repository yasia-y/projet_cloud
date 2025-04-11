# This module contains all the plotting logic for the dashboard.
# Use libraries like matplotlib or plotly to generate visualizations from the sensor data.

import streamlit as st
import matplotlib.pyplot as plt

def plot_temperature_humidity(df):
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.set_xlabel('Temps')
    ax1.set_ylabel('Température (°C)', color='tab:red')
    ax1.plot(df['timestamp'], df['temperature'], color='tab:red', label='Température')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    ax2 = ax1.twinx()  # Deuxième axe Y
    ax2.set_ylabel('Humidité (%)', color='tab:blue')
    ax2.plot(df['timestamp'], df['humidity'], color='tab:blue', label='Humidité')
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    fig.tight_layout()
    st.pyplot(fig)

