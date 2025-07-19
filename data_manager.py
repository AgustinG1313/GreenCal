import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONSTANTES DE ARCHIVOS ---
# Definimos los nombres de los archivos aquí para no cometer errores de tipeo más adelante.
# Es una buena práctica para mantener el código limpio y fácil de modificar.
REGISTROS_FILE = "registros.txt"
ELECTRODOMESTICOS_FILE = "electrodomesticos.txt"

# --- FUNCIONES PARA GESTIONAR LAS FACTURAS ---

# Este decorador es nuestra primera y más importante herramienta de Green Software.
# Le dice a Streamlit: "Oye, ejecuta esta función una vez y guarda el resultado en memoria".
# No volverá a leer el archivo del disco a menos que se lo indiquemos, ahorrando
# muchísima energía y haciendo que la app sea increíblemente rápida.
@st.cache_data
def load_records():
    """
    Carga los registros de facturas desde el archivo registros.txt.
    Gracias a @st.cache_data, esta operación de lectura de disco solo
    ocurrirá cuando sea estrictamente necesario.
    """
    try:
        # Intentamos leer el archivo. Le asignamos nombres a las columnas.
        df = pd.read_csv(REGISTROS_FILE, names=["Fecha", "Consumo (kWh)", "Costo (ARS)"])
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Si el archivo no existe o está vacío, creamos un DataFrame (una tabla)
        # vacío con las columnas correctas. Esto evita que la aplicación se rompa.
        return pd.DataFrame(columns=["Fecha", "Consumo (kWh)", "Costo (ARS)"])

def save_record(consumo, costo):
    """
    Guarda un nuevo registro de factura en el archivo y, muy importante,
    le dice a Streamlit que la próxima vez que se necesiten los datos,
    debe volver a leerlos.
    """
    # Usamos 'a' para "append" (añadir), para no borrar los datos existentes.
    with open(REGISTROS_FILE, "a") as f:
        # Escribimos una nueva línea en formato CSV: fecha,consumo,costo
        f.write(f"{datetime.now().strftime('%Y-%m-%d')},{consumo},{costo}\n")
    
    # Esta línea es la pareja de @st.cache_data. Le decimos: "Olvida lo que
    # recordabas de load_records(), porque los datos han cambiado".
    st.cache_data.clear()

# --- FUNCIONES PARA GESTIONAR LOS ELECTRODOMÉSTICOS ---
# Las dejamos listas para cuando las necesitemos en fases posteriores.

@st.cache_data
def load_appliances():
    """
    Carga la lista de electrodomésticos desde el archivo.
    Usamos el mismo principio de caché para la eficiencia.
    """
    try:
        # Leemos un archivo donde cada línea es un objeto JSON.
        df = pd.read_json(ELECTRODOMESTICOS_FILE, lines=True)
        # Lo convertimos a una lista de diccionarios, que es más fácil de manejar.
        return df.to_dict('records')
    except (FileNotFoundError, ValueError):
        # Si no hay archivo o está vacío, devolvemos una lista vacía.
        return []

def save_appliance(new_appliance):
    """Guarda un nuevo electrodoméstico y limpia la caché."""
    with open(ELECTRODOMESTICOS_FILE, "a") as f:
        # Convertimos el diccionario del nuevo electrodoméstico a un string JSON y lo guardamos.
        f.write(pd.Series(new_appliance).to_json() + '\n')
    st.cache_data.clear()