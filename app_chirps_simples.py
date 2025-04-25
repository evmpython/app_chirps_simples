import streamlit as st
import geemap.foliumap as geemap  # Importação correta para Streamlit
import ee

# Inicializar o Google Earth Engine
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

    
# Configuração do aplicativo
st.set_page_config(layout="wide")
st.title("Visualizador de Precipitação Diária - CHIRPS (Brasil)")

#========================================================================================================================#
#                                          FILTRA REGIÃO DE INTERESSE
#========================================================================================================================#
roi = ee.FeatureCollection('FAO/GAUL/2015/level0').filter(ee.Filter.eq('ADM0_NAME', 'Brazil'))

#========================================================================================================================#
#                                            CARREGA OS DADOS
#========================================================================================================================#
# carrega os dados
chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
           .filterDate('2025-01-01', '2025-01-02') \
           .select('precipitation') \
           .filterBounds(roi)

#========================================================================================================================#
#                                           PLOTA FIGURA
#========================================================================================================================#
# cria a moldura do mapa
Map = geemap.Map(height="450px", width="800px")

# centraliza o mapa na região
Map.centerObject(roi)

# parâmetros de visualização
vis = {'min': 0, 'max': 30, 'palette': ['000096','0064ff', '00b4ff', '33db80', '9beb4a', 'ffeb00', 'ffb300', 'ff6400', 'eb1e00', 'af0000']}

# plota mapa
Map.addLayer(chirps.sum().clip(roi), vis, 'Mapa de Precipitação')
#Map.addLayer(chirps.sum(), vis, 'Mapa de Precipitação')

# contorno da região
style1 = {'color': 'black', 'fillColor': '00000000'}
Map.addLayer(roi.style(**style1), {}, 'Brasil')

# barra de cores
#Map.add_colorbar_branca(colors=vis['palette'], vmin=vis['min'], vmax=vis['max'], layer_name='Precipitação (mm)')

# exibe na tela
Map.to_streamlit(height=600)