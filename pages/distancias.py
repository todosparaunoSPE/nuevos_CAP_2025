# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 17:09:11 2025

@author: jperezr
"""

import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic


# Título de la aplicación
st.title("Distancias de los minicipos de un Estado a la ubicación propuesta por K_Means")

st.sidebar.write("Nombre: Javier Horacio Pérez Ricárdez")

# Cargar archivo automáticamente
@st.cache_data
def load_data():
    df = pd.read_csv("distancias.csv")
    return df

def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

# Cargar datos
df = load_data()

# Calcular distancias
df["DISTANCIA_KM"] = df.apply(lambda row: calculate_distance(row["LATITUD"], row["LONGITUD"], 
                                                              row["LATITUD_1"], row["LONGITUD_1"]), axis=1)

# Filtrar por estado y municipio
estado_seleccionado = st.selectbox("Selecciona un estado", options=df["ESTADO"].unique())
df_filtrado = df[df["ESTADO"] == estado_seleccionado]

# Selección múltiple con todos los municipios por defecto
municipios_seleccionados = st.multiselect("Selecciona los municipios (todos seleccionados por defecto, elimina los que no quieras)", 
                                          options=df_filtrado["MUNICIPIO"].unique(), 
                                          default=df_filtrado["MUNICIPIO"].unique())

if municipios_seleccionados:
    df_filtrado = df_filtrado[df_filtrado["MUNICIPIO"].isin(municipios_seleccionados)]

# Agregar fila con la suma de PEA y DISTANCIA_KM
suma_pea = df_filtrado["PEA"].sum()
suma_distancia = df_filtrado["DISTANCIA_KM"].sum()
suma_fila = pd.DataFrame({"ESTADO": ["TOTAL"], "MUNICIPIO": ["TOTAL"], "PEA": [suma_pea], "DISTANCIA_KM": [suma_distancia]})
df_filtrado = pd.concat([df_filtrado, suma_fila], ignore_index=True)

# Mostrar DataFrame
st.dataframe(df_filtrado)
