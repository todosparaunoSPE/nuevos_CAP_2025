# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 13:38:34 2025

@author: jperezr
"""

import streamlit as st
import pandas as pd
import folium
import os

# Título de la aplicación
st.title("Visualización de Datos y Mapa Interactivo")

st.sidebar.write("Nombre: Javier Horacio Pérez Ricárdez")

# 1. Cargar automáticamente el archivo PENSIONISSSTE_Y_MODELO.csv
@st.cache_data  # Cachear para mejorar el rendimiento
def load_data():
    # Verificar si el archivo existe
    if os.path.exists("PENSIONISSSTE_Y_MODELO.csv"):
        data = pd.read_csv("PENSIONISSSTE_Y_MODELO.csv")
        return data
    else:
        st.error("El archivo 'PENSIONISSSTE_Y_MODELO.csv' no se encuentra en el directorio actual.")
        return None

# Cargar los datos
df = load_data()

# 2. Mostrar todos los datos en un DataFrame
if df is not None:
    st.write("Datos cargados:")
    st.dataframe(df)

    # 3. Crear un mapa interactivo en HTML
    st.write("### Mapa Interactivo")

    # Crear el mapa centrado en el primer punto
    if not df.empty:
        mapa = folium.Map(location=[df['LATITUD'].mean(), df['LONGITUD'].mean()], zoom_start=6)

        # 4. Colorear los PINs según el valor de la columna MUNICIPIO
        for idx, row in df.iterrows():
            municipio = row['MUNICIPIO']
            latitud = row['LATITUD']
            longitud = row['LONGITUD']

            # Definir el color del PIN
            if municipio == "PENSIONISSSTE":
                color = "red"
            elif municipio == "Nuevo CAP":
                color = "blue"
            else:
                color = "gray"  # Color por defecto para otros municipios

            # Agregar el marcador al mapa
            folium.Marker(
                location=[latitud, longitud],
                popup=f"Municipio: {municipio}<br>Latitud: {latitud}<br>Longitud: {longitud}",
                icon=folium.Icon(color=color)
            ).add_to(mapa)

        # Mostrar el mapa en Streamlit
        st.components.v1.html(mapa._repr_html_(), height=500)

        # 5. Botón para descargar el mapa en formato HTML
        st.write("### Descargar Mapa")
        map_path = "mapa_interactivo.html"
        mapa.save(map_path)

        with open(map_path, "rb") as file:
            btn = st.download_button(
                label="Descargar Mapa en HTML",
                data=file,
                file_name=map_path,
                mime="application/html"
            )
    else:
        st.warning("El DataFrame está vacío. No se puede crear el mapa.")
else:
    st.warning("No se pudieron cargar los datos. Verifica el archivo CSV.")
