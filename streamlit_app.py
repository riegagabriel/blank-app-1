import streamlit as st
import zipfile
import tempfile
import os
from streamlit.components.v1 import html

st.set_page_config(layout="wide")

st.title("Mapa Folium - IIEE y Extorsión")

ZIP_FILE = "mapa_iiee_extorsion.zip"

# Crear carpeta temporal
with tempfile.TemporaryDirectory() as temp_dir:

    # Descomprimir ZIP
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Buscar archivo HTML dentro del ZIP
    html_file = None

    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith(".html"):
                html_file = os.path.join(root, file)
                break

    if html_file is None:
        st.error("No se encontró un archivo HTML dentro del ZIP.")
    else:
        # Leer HTML
        with open(html_file, "r", encoding="utf-8") as f:
            source_code = f.read()

        # Mostrar mapa
        html(source_code, height=800, scrolling=True)
