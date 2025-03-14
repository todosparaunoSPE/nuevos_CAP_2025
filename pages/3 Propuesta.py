# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 13:43:25 2025

@author: jperezr
"""

import streamlit as st
import pandas as pd
import folium
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
import numpy as np
import os

# Título de la aplicación
st.title("Propuesta de 5 Nuevas Ubicaciones de CAP")

# Sidebar con sección de ayuda y tu nombre
with st.sidebar:
    st.header("Ayuda")
    st.write("""
    Esta aplicación utiliza el modelo de K-Means para proponer 5 nuevas ubicaciones de CAP basadas en la distribución geográfica de los municipios.
    - **PIN Rojo**: Municipio PENSIONISSSTE.
    - **PIN Verde**: Municipios AZTECA, CITIBANAMEX, COPPEL, INBURSA, INVERCAP, PRINCIPAL, PROFUTURO, SURA, XXI-BANORTE.
    - **PIN Negro**: Otros municipios.
    - **PIN Azul**: Ubicaciones sugeridas para nuevos CAP.
    """)
    st.write("Desarrollado por: **Javier Horacio Pérez Ricárdez**")

# 1. Cargar automáticamente el archivo PENSIONISSSTE_Y_MODELO.csv
@st.cache_data
def load_data():
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

    # Verificar si las columnas necesarias están presentes
    required_columns = ['ESTADO', 'MUNICIPIO', 'LATITUD', 'LONGITUD']
    if not all(column in df.columns for column in required_columns):
        st.error(f"El archivo CSV debe contener las columnas: {required_columns}")
    else:
        # 3. Aplicar K-Means para encontrar 5 ubicaciones sugeridas
        if not df.empty:
            # Seleccionar las columnas relevantes (latitud, longitud)
            X = df[['LATITUD', 'LONGITUD']]

            # Aplicar K-Means con 5 clusters
            kmeans = KMeans(n_clusters=5, random_state=42)
            kmeans.fit(X)

            # Obtener las coordenadas de los centroides (ubicaciones sugeridas)
            centroides = kmeans.cluster_centers_

            # Crear un DataFrame con las 5 ubicaciones sugeridas
            ubicaciones_sugeridas_df = pd.DataFrame(centroides, columns=['LATITUD', 'LONGITUD'])
            ubicaciones_sugeridas_df['CAP'] = [f"CAP {i+1}" for i in range(5)]  # Agregar nombres a los CAP

            # 4. Asignar el estado y municipio más cercano a cada propuesta
            def asignar_estado_municipio(propuestas, municipios):
                # Calcular la distancia entre cada propuesta y todos los municipios
                distancias = cdist(propuestas[['LATITUD', 'LONGITUD']], municipios[['LATITUD', 'LONGITUD']])
                
                # Encontrar el índice del municipio más cercano para cada propuesta
                indices_mas_cercanos = np.argmin(distancias, axis=1)
                
                # Asignar el estado y municipio más cercano
                propuestas['ESTADO'] = municipios.iloc[indices_mas_cercanos]['ESTADO'].values
                propuestas['MUNICIPIO'] = municipios.iloc[indices_mas_cercanos]['MUNICIPIO'].values
                return propuestas

            # Asignar estado y municipio a las 5 propuestas
            ubicaciones_sugeridas_df = asignar_estado_municipio(ubicaciones_sugeridas_df, df)

            # Mostrar las 5 ubicaciones sugeridas con estado y municipio
            st.write("### 5 Ubicaciones Sugeridas para Nuevos CAP")
            st.dataframe(ubicaciones_sugeridas_df)

            # 5. Crear el mapa con Folium
            mapa = folium.Map(location=[df['LATITUD'].mean(), df['LONGITUD'].mean()], zoom_start=6)

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

            # Agregar marcadores para los municipios existentes
            for idx, row in df.iterrows():
                municipio = row['MUNICIPIO'].strip().upper()
                color = colores_municipios.get(municipio, 'black')  # Negro por defecto

                folium.Marker(
                    location=[row['LATITUD'], row['LONGITUD']],
                    popup=f"Municipio: {municipio}<br>Latitud: {row['LATITUD']}<br>Longitud: {row['LONGITUD']}",
                    icon=folium.Icon(color=color)
                ).add_to(mapa)

            # Agregar marcadores para las 5 ubicaciones sugeridas (azul)
            for idx, row in ubicaciones_sugeridas_df.iterrows():
                folium.Marker(
                    location=[row['LATITUD'], row['LONGITUD']],
                    popup=f"{row['CAP']}<br>Estado: {row['ESTADO']}<br>Municipio: {row['MUNICIPIO']}",
                    icon=folium.Icon(color='blue')
                ).add_to(mapa)

            # Mostrar el mapa en Streamlit
            st.write("### Mapa de Ubicaciones Sugeridas")
            st.components.v1.html(mapa._repr_html_(), height=500)

            # 6. Botón para descargar el mapa y los datos
            st.write("### Descargar Resultados")

            # Guardar el mapa en un archivo HTML
            map_path = "mapa_5_cap.html"
            mapa.save(map_path)

            with open(map_path, "rb") as file:
                btn_map = st.download_button(
                    label="Descargar Mapa en HTML",
                    data=file,
                    file_name=map_path,
                    mime="application/html"
                )

            # Guardar las 5 ubicaciones sugeridas en un archivo CSV
            csv_path = "ubicaciones_sugeridas.csv"
            ubicaciones_sugeridas_df.to_csv(csv_path, index=False)

            with open(csv_path, "rb") as file:
                btn_csv = st.download_button(
                    label="Descargar Ubicaciones Sugeridas en CSV",
                    data=file,
                    file_name=csv_path,
                    mime="text/csv"
                )
        else:
            st.warning("El DataFrame está vacío. No se puede crear el mapa.")
else:
    st.warning("No se pudieron cargar los datos. Verifica el archivo CSV.")