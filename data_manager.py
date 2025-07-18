import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONSTANTES DE ARCHIVOS ---
# Centralizar los nombres de archivo evita errores de tipeo en el futuro.
REGISTROS_FILE = "registros.txt"
ELECTRODOMESTICOS_FILE = "electrodomesticos.txt"

# --- FUNCIONES PARA FACTURAS ---

@st.cache_data # ¡Clave para la eficiencia! No releer en cada acción del usuario.
def load_records():
    """
    Carga los registros de facturas desde un archivo CSV.
    Esta función está cacheada, por lo que solo leerá del disco la primera vez
    o cuando la caché sea invalidada explícitamente.
    """
    try:
        df = pd.read_csv(REGISTROS_FILE, names=["Fecha", "Consumo (kWh)", "Costo (ARS)"])
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Manejo robusto de errores: si no hay archivo o está vacío, devuelve un DataFrame limpio.
        return pd.DataFrame(columns=["Fecha", "Consumo (kWh)", "Costo (ARS)"])

def save_record(consumo, costo):
    """Guarda un nuevo registro de factura y limpia la caché de registros."""
    with open(REGISTROS_FILE, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d')},{consumo},{costo}\n")
    # Invalida la caché de load_records() para que la próxima llamada a esa función
    # se vea forzada a releer el archivo y obtener los datos actualizados.
    st.cache_data.clear()

# --- FUNCIONES PARA ELECTRODOMÉSTICOS ---

@st.cache_data
def load_appliances():
    """
    Carga la lista de electrodomésticos desde un archivo JSONL (JSON Lines).
    Cacheado por la misma razón que load_records.
    """
    try:
        # Usamos read_json con lines=True para leer un archivo donde cada línea es un objeto JSON.
        # Esto es más eficiente para añadir registros que leer y reescribir un archivo JSON completo.
        df = pd.read_json(ELECTRODOMESTICOS_FILE, lines=True)
        return df.to_dict('records')
    except (FileNotFoundError, ValueError):
        return []

def save_appliance(new_appliance):
    """Guarda un nuevo electrodoméstico y limpia la caché."""
    with open(ELECTRODOMESTICOS_FILE, "a") as f:
        # Convertimos el diccionario a una serie de pandas y luego a JSON para guardarlo.
        f.write(pd.Series(new_appliance).to_json() + '\n')
    st.cache_data.clear()
