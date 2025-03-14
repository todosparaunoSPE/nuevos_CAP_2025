# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:32:00 2025

@author: jperezr
"""

import streamlit as st
import pandas as pd
import folium
from sklearn.cluster import KMeans
import numpy as np

# Cargar el archivo CSV
@st.cache_data
def load_data():
    data = pd.read_csv('BASE_UTILIZADA_2025.csv')
    return data

# Mostrar todos los datos en el DataFrame
df = load_data()

# Título de la aplicación
st.title("Modelo de Huff Mejorado con K-Means")

# Sidebar con sección de ayuda y tu nombre
with st.sidebar:
    st.header("Ayuda")
    st.write("""
    Esta aplicación utiliza el modelo de K-Means para sugerir una ubicación óptima basada en la PEA (Población Económicamente Activa) de los municipios de un estado seleccionado.
    - **PIN Rojo**: Municipio PENSIONISSSTE.
    - **PIN Verde**: Municipios AZTECA, CITIBANAMEX, COPPEL, INBURSA, INVERCAP, PRINCIPAL, PROFUTURO, SURA, XXI-BANORTE.
    - **PIN Negro**: Otros municipios.
    - **PIN Azul**: Ubicación sugerida por K-Means.
    """)
    st.write("Desarrollado por: **Javier Horacio Pérez Ricárdez**")  # Reemplaza "Tu Nombre" con tu nombre real.

# Selectbox para filtrar por ESTADO
estado_seleccionado = st.selectbox('Selecciona un estado', df['ESTADO'].unique())

# Filtrar los datos según el estado seleccionado
df_filtrado = df[df['ESTADO'] == estado_seleccionado].copy()

# Mostrar los datos filtrados
st.write(f"Datos filtrados para el estado de {estado_seleccionado}:")
st.dataframe(df_filtrado)

# Aplicar K-Means para encontrar la ubicación sugerida
if not df_filtrado.empty:
    # Seleccionar las columnas relevantes (latitud, longitud, PEA)
    X = df_filtrado[['LATITUD', 'LONGITUD', 'PEA']]

    # Aplicar K-Means para encontrar el centroide (ubicación sugerida)
    kmeans = KMeans(n_clusters=1, random_state=42)
    kmeans.fit(X)

    # Obtener el centroide (ubicación sugerida)
    centroide = kmeans.cluster_centers_[0]
    latitude_sugerida = centroide[0]
    longitude_sugerida = centroide[1]

    # Mostrar la ubicación sugerida por K-Means
    st.write("Ubicación sugerida por K-Means:")
    st.write(f"Latitud: {latitude_sugerida}, Longitud: {longitude_sugerida}")

    # Crear un DataFrame con la ubicación sugerida
    ubicacion_sugerida_df = pd.DataFrame({
        'ESTADO': [estado_seleccionado],
        'LATITUD': [latitude_sugerida],
        'LONGITUD': [longitude_sugerida]
    })
    st.write("Detalles de la ubicación sugerida:")
    st.dataframe(ubicacion_sugerida_df)

    # Crear el mapa con Folium
    m = folium.Map(location=[latitude_sugerida, longitude_sugerida], zoom_start=6)

    # Diccionario de colores para los municipios
    colores_municipios = {
        'PENSIONISSSTE': 'red',
        'AZTECA': 'green',
        'CITIBANAMEX': 'green',
        'COPPEL': 'green',
        'INBURSA': 'green',
        'INVERCAP': 'green',
        'PRINCIPAL': 'green',
        'PROFUTURO': 'green',
        'SURA': 'green',
        'XXI-BANORTE': 'green'
    }

    # Agregar marcadores para los municipios
    for idx, row in df_filtrado.iterrows():
        municipio = row['MUNICIPIO'].strip().upper()  # Normalizar el nombre del municipio
        color = colores_municipios.get(municipio, 'black')  # Negro por defecto

        folium.Marker(
            location=[row['LATITUD'], row['LONGITUD']],
            popup=f"Municipio: {municipio}<br>PEA: {row['PEA']}",
            icon=folium.Icon(color=color)
        ).add_to(m)

    # Agregar el marcador para la ubicación sugerida (azul)
    folium.Marker(
        location=[latitude_sugerida, longitude_sugerida],
        popup="Ubicación sugerida por K-Means",
        icon=folium.Icon(color='blue')
    ).add_to(m)

    # Mostrar el mapa en Streamlit
    st.write(f"Mapa de los municipios en {estado_seleccionado} con la ubicación sugerida:")
    st.components.v1.html(m._repr_html_(), height=500)

    # Guardar el mapa en un archivo HTML
    map_path = f'mapa_{estado_seleccionado}_kmeans.html'
    m.save(map_path)

    # Botón para descargar el mapa
    with open(map_path, "rb") as file:
        btn = st.download_button(
            label=f"Descargar el mapa de {estado_seleccionado} con la ubicación sugerida en HTML",
            data=file,
            file_name=map_path,
            mime="application/html"
        )

    # Análisis justificativo de la ubicación sugerida
    st.write("### Análisis Justificativo de la Ubicación Sugerida")

    # Calcular la PEA normalizada
    df_filtrado['PEA_normalizada'] = df_filtrado['PEA'] / df_filtrado['PEA'].sum()

    # Calcular las contribuciones ponderadas de latitud y longitud
    df_filtrado['Latitud_Ponderada'] = df_filtrado['LATITUD'] * df_filtrado['PEA_normalizada']
    df_filtrado['Longitud_Ponderada'] = df_filtrado['LONGITUD'] * df_filtrado['PEA_normalizada']

    # Crear un DataFrame con el análisis
    analisis_df = df_filtrado[['MUNICIPIO', 'LATITUD', 'LONGITUD', 'PEA', 'PEA_normalizada', 'Latitud_Ponderada', 'Longitud_Ponderada']]

    # Mostrar el DataFrame con el análisis
    st.write("Detalles del análisis para justificar la ubicación sugerida:")
    st.dataframe(analisis_df)

    # Explicación del cálculo
    st.write("""
    **Explicación del cálculo:**
    - **PEA Normalizada**: Es la PEA de cada municipio dividida por la suma total de la PEA en el estado. Representa el peso relativo de cada municipio.
    - **Latitud Ponderada y Longitud Ponderada**: Son las coordenadas de cada municipio multiplicadas por su PEA normalizada. Estas contribuciones ponderadas se suman para obtener la ubicación sugerida.
    - **Ubicación Sugerida**: Es el promedio ponderado de las coordenadas de los municipios, donde los pesos son las PEA normalizadas.
    """)

else:
    st.warning(f"No hay datos disponibles para el estado de {estado_seleccionado}.")