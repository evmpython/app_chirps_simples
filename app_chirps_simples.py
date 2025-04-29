import streamlit as st
import geemap
import ee
from datetime import datetime, timedelta

# Configuração inicial da página
st.set_page_config(
    layout="wide", page_title="Visualizador de Precipitação Diária - CHIRPS (Brasil)")
st.title("🌧️ Visualizador de Precipitação Diária - CHIRPS (Brasil)")

# Inicialização do Earth Engine


def initialize_earth_engine():
    try:
        if not ee.data._credentials:
            ee.Authenticate()
        ee.Initialize()
        return True
    except Exception as e:
        st.error(f"Erro ao inicializar o Earth Engine: {e}")
        return False


if not initialize_earth_engine():
    st.stop()

# Interface do usuário
col1, col2 = st.columns([1, 3])
with col1:
    st.subheader("Configurações")

    max_date = datetime.now() - timedelta(days=60)
    default_date = max_date - timedelta(days=1)

    selected_date = st.date_input(
        "Selecione a data",
        value=default_date,
        max_value=max_date,
        help="Dados CHIRPS têm um delay de 2 meses. Selecione uma data até 60 dias antes da data atual."
    )

    end_date = selected_date + timedelta(days=1)

    palette_options = {
        'Padrão CHIRPS': ['000096', '0064ff', '00b4ff', '33db80', '9beb4a', 'ffeb00', 'ffb300', 'ff6400', 'eb1e00', 'af0000'],
        'Azul a Vermelho': ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'],
        'Precipitação Intensa': ['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494']
    }

    selected_palette = st.selectbox(
        "Escala de cores", list(palette_options.keys()), index=0)
    vmin = st.slider("Valor mínimo (mm)", 0, 10, 0)
    vmax = st.slider("Valor máximo (mm)", 10, 100, 30)

# Carregamento dos dados do CHIRPS
try:
    roi = ee.FeatureCollection(
        'FAO/GAUL/2015/level0').filter(ee.Filter.eq('ADM0_NAME', 'Brazil'))
    date_str = selected_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    chirps_data = (
        ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        .filterDate(date_str, end_date_str)
        .select('precipitation')
        .filterBounds(roi)
    )

    count = chirps_data.size().getInfo()
    if count == 0:
        st.error(f"Não há dados disponíveis para {date_str}")
        st.stop()

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Visualização do mapa
with col2:
    st.subheader(
        f"Mapa de Precipitação para {selected_date.strftime('%d/%m/%Y')}")

    try:
        Map = geemap.Map(height=600, width="100%")
        Map.centerObject(roi, zoom=4)

        vis_params = {
            'min': vmin,
            'max': vmax,
            'palette': palette_options[selected_palette]
        }

        precipitation = chirps_data.sum().clip(roi)
        Map.addLayer(precipitation, vis_params, 'Precipitação (mm)')
        Map.addLayer(
            roi.style(**{'color': 'black', 'fillColor': '00000000'}), {}, 'Brasil')

        Map.add_colorbar(
            vis_params,
            label="Precipitação (mm)",
            layer_name="Precipitação Diária",
            orientation="horizontal",
            position="bottomright"
        )
        Map.addLayerControl()

        # Exibe o mapa no Streamlit
        Map.to_streamlit()

    except Exception as e:
        st.error(f"Erro ao gerar o mapa: {e}")

# Informações adicionais
st.markdown("---")
with st.expander("ℹ️ Sobre os dados e o aplicativo"):
    st.markdown("""
    **Fonte de dados:** [CHIRPS Daily](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY)  
    **Resolução espacial:** 0.05° (~5km)  
    **Cobertura temporal:** Desde 1981 até presente  
    **Atualização dos dados:** Delay de aproximadamente 2 meses

    **Observação:** O sistema considera a data inicial selecionada até o dia seguinte (data inicial + 1 dia)
    """)

st.markdown("---")
st.caption("**Desenvolvido por:** Enrique V. Mattos")
st.caption("**Última atualização:** 29/04/2025")
st.caption("**Desenvolvido com:** Google Earth Engine, geemap e Streamlit")
