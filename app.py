import streamlit as st
from streamlit_option_menu import option_menu
# Importamos nuestro módulo de datos para poder usar sus funciones.
import data_manager as dm 

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTADO ---
st.set_page_config(page_title="GreenCalc", page_icon="♻️", layout="centered")

# Usamos @st.cache_resource para el CSS porque el recurso (el archivo) no cambia.
# Esto asegura que el archivo CSS se lee del disco solo una vez por sesión.
@st.cache_resource
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css('style.css')

# st.session_state es como la memoria a corto plazo de la app.
# Este bloque if se ejecuta solo una vez cuando un usuario abre la app.
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.appliances = dm.load_appliances()
    # Añadimos una variable para controlar qué formulario mostrar: 'login' o 'register'
    st.session_state.page = 'login'

# --- 2. DEFINICIÓN DE PÁGINAS ---

def show_login_page():
    """
    Muestra la página de inicio de sesión o registro, según el estado de st.session_state.page.
    """
    st.title("Bienvenido a GreenCalc ♻️")
    st.markdown("Tu asistente para un futuro más sostenible.")

    # --- Lógica para cambiar entre Login y Registro ---
    if st.session_state.page == 'login':
        # --- Formulario de Inicio de Sesión ---
        with st.form("login_form"):
            st.header("Iniciar Sesión")
            email = st.text_input("Correo Electrónico (simulado)")
            password = st.text_input("Contraseña (simulada)", type="password")
            submitted = st.form_submit_button("Ingresar")

            if submitted:
                if email and password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = email.split('@')[0].capitalize()
                    st.rerun() 
                else:
                    st.error("Por favor, completa ambos campos.")
        
        # Enlace para cambiar al formulario de registro
        st.info("¿No tienes una cuenta?")
        if st.button("Regístrate aquí"):
            st.session_state.page = 'register'
            st.rerun() 

    elif st.session_state.page == 'register':
        # --- Formulario de Registro ---
        with st.form("register_form"):
            st.header("Registro")
            nombre = st.text_input("Nombre y Apellido")
            email_reg = st.text_input("Correo Electrónico")
            password_reg = st.text_input("Contraseña", type="password")
            submitted_reg = st.form_submit_button("Registrarse")

            if submitted_reg:
                if nombre and email_reg and password_reg:
                    st.session_state.logged_in = True
                    st.session_state.current_user = nombre.split(' ')[0].capitalize()
                    st.session_state.page = 'login' # Resetear por si vuelve a desloguearse
                    st.rerun() 
                else:
                    st.error("Por favor, completa todos los campos.")
        
        # Enlace para volver al formulario de login
        st.info("¿Ya tienes una cuenta?")
        if st.button("Inicia sesión"):
            st.session_state.page = 'login'
            st.rerun() 
            
    # --- Bypass para desarrolladores ---
    st.divider()
    if st.button("Bypass de desarrollador (Entrar como Admin)"):
        st.session_state.logged_in = True
        st.session_state.current_user = "Admin"
        st.rerun() 


def show_panel_page():
    st.title("Panel de Control (en construcción)")

def show_facturas_page():
    """
    Muestra la interfaz para gestionar las facturas de consumo eléctrico.
    """
    st.title("Gestión de Facturas 🧾")
    st.markdown("Registra tus facturas para un seguimiento preciso de tu consumo y gasto.")

    # --- Formulario para añadir una nueva factura ---
    with st.form("factura_form"):
        st.subheader("Agregar Nuevo Registro de Factura")
        
        col1, col2 = st.columns(2)
        
        with col1:
            consumo_kwh = st.number_input("Consumo de la Factura (kWh)", min_value=0.0, format="%.2f")
        
        with col2:
            costo_ars = st.number_input("Costo Total de la Factura (ARS)", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Guardar Registro")
        
        if submitted:
            if consumo_kwh > 0:
                dm.save_record(consumo_kwh, costo_ars)
                st.success("¡Factura registrada con éxito!")
            else:
                st.warning("Por favor, ingresa un valor de consumo mayor a cero.")
    
    st.divider()

    # --- Historial de Registros ---
    st.subheader("Historial de Consumos")
    
    df_records = dm.load_records()
    
    if df_records.empty:
        st.info("Aún no has registrado ninguna factura. ¡Empieza añadiendo una!")
    else:
        st.dataframe(df_records, use_container_width=True)

        # --- Conciencia del Carbono: Dando Contexto ---
        avg_consumo_usuario = df_records["Consumo (kWh)"].mean()
        
        col1, col2 = st.columns(2)
        col1.metric(label="Tu Consumo Promedio Mensual", value=f"{avg_consumo_usuario:.1f} kWh")
        
        consumo_promedio_chaco = 250
        diferencia = avg_consumo_usuario - consumo_promedio_chaco
        col2.metric(label="Promedio Provincial (Chaco)", value=f"{consumo_promedio_chaco} kWh", delta=f"{diferencia:.1f} kWh")
        
        st.caption("El 'delta' muestra tu consumo en comparación con el promedio de la provincia. Un número negativo significa que consumes menos que el promedio. ¡Bien hecho!")

def show_electrodomesticos_page():
    """
    Muestra un panel interactivo para que el usuario añada sus electrodomesticos.
    """
    st.title("Añadir Electrodomésticos a tu Inventario 🔌")
    st.markdown("Haz clic en un aparato para configurarlo y añadirlo a tu lista personal.")

    # Base de datos ampliada con consumo en Standby (basado en los documentos)
    APPLIANCE_DB = {
        "Heladera": {"potencia_w": 150, "emoji": "🧊", "standby_w": 2},
        "Aire Acondicionado": {"potencia_w": 878, "emoji": "❄️", "standby_w": 3},
        "Lavadora": {"potencia_w": 500, "emoji": "🧺", "standby_w": 1},
        "Horno Eléctrico": {"potencia_w": 1500, "emoji": "🔥", "standby_w": 2},
        "Lámpara LED": {"potencia_w": 11, "emoji": "💡", "standby_w": 0},
        "Computadora": {"potencia_w": 200, "emoji": "💻", "standby_w": 5},
        "Laptop/Notebook": {"potencia_w": 60, "emoji": " portátil", "standby_w": 3},
        "Pava Eléctrica": {"potencia_w": 2000, "emoji": "🫖", "standby_w": 0},
        "Cargador de Celular": {"potencia_w": 5, "emoji": "📱", "standby_w": 1},
        "Router WiFi": {"potencia_w": 10, "emoji": "📶", "standby_w": 0},
        "Monitor": {"potencia_w": 22, "emoji": "🖥️", "standby_w": 2},
        "Plancha": {"potencia_w": 1500, "emoji": "ủi", "standby_w": 0},
        "Televisor": {"potencia_w": 120, "emoji": "📺", "standby_w": 4},
        "Microondas": {"potencia_w": 1100, "emoji": "🍲", "standby_w": 3},
    }

    # --- Función para el Diálogo de Configuración Detallada ---
    @st.dialog("Configurar Electrodoméstico")
    def appliance_dialog(tipo, data):
        st.markdown(f"### {data['emoji']} Configura tu {tipo}")
        
        # --- NUEVOS CAMPOS DETALLADOS ---
        # El usuario puede ajustar la potencia si conoce el valor exacto de su modelo.
        potencia_w_editable = st.number_input("Potencia (Watts)", min_value=1, value=data['potencia_w'], key=f"potencia_{tipo}")
        
        # El "consumo fantasma" es clave para la conciencia energética.
        standby_w = st.number_input("Consumo en Standby/Vampiro (Watts)", min_value=0, value=data.get('standby_w', 0), key=f"standby_{tipo}")
        
        cantidad = st.number_input("Cantidad de aparatos", min_value=1, step=1, key=f"cantidad_{tipo}")
        horas_dia = st.number_input("Horas de uso al día", min_value=0.0, max_value=24.0, value=1.0, step=0.5, key=f"horas_{tipo}")
        dias_semana = st.number_input("Días de uso a la semana", min_value=1, max_value=7, value=7, step=1, key=f"dias_{tipo}")
        
        # Un slider es más intuitivo para seleccionar meses.
        meses_uso = st.slider("Meses de uso al año", min_value=1, max_value=12, value=12, key=f"meses_{tipo}")

        if st.button("Añadir a mi inventario", key=f"btn_{tipo}"):
            new_appliance = {
                "tipo": tipo,
                "cantidad": cantidad,
                "horas_dia": horas_dia,
                "dias_semana": dias_semana,
                "potencia_w": potencia_w_editable,
                "standby_w": standby_w,
                "meses_uso": meses_uso
            }
            dm.save_appliance(new_appliance)
            st.session_state.appliances.append(new_appliance)
            st.success(f"¡{cantidad}x {tipo} añadido(s)!")
            st.rerun()

    # --- Panel de Selección de Electrodomésticos (Volvemos al diseño de botones) ---
    st.markdown('<div class="appliance-grid">', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (tipo, data) in enumerate(APPLIANCE_DB.items()):
        with cols[i % 5]:
            if st.button(f"{data['emoji']}\n{tipo}", key=tipo, use_container_width=True):
                appliance_dialog(tipo, data)
                
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # --- Inventario Personal del Usuario ---
    st.subheader("Tu Inventario Actual")
    if not st.session_state.appliances:
        st.info("Tu inventario está vacío. Haz clic en un aparato de arriba para empezar.")
    else:
        for appliance in st.session_state.appliances:
            with st.container(border=True):
                # --- CÁLCULO ACTUALIZADO Y MÁS PRECISO ---
                # Horas totales de uso activo al mes
                horas_activas_mes = appliance['horas_dia'] * appliance['dias_semana'] * 4.345
                # Horas totales en standby al mes (total de horas menos las activas)
                horas_standby_mes = (24 * 30.4) - horas_activas_mes
                
                # Consumo activo en kWh
                consumo_activo_kwh = (appliance['potencia_w'] * horas_activas_mes) / 1000
                # Consumo standby en kWh
                consumo_standby_kwh = (appliance.get('standby_w', 0) * horas_standby_mes) / 1000
                
                # Consumo total mensual, ajustado por los meses de uso al año
                consumo_total_mensual = (consumo_activo_kwh + consumo_standby_kwh) * (appliance.get('meses_uso', 12) / 12)
                
                col1, col2 = st.columns([3, 1])
                col1.markdown(f"**{appliance['cantidad']}x {appliance['tipo']}** ({appliance['horas_dia']}h/día, {appliance['meses_uso']}/12 meses)")
                col2.metric(label="Consumo Est.", value=f"{consumo_total_mensual:.2f} kWh/mes")

def show_tips_page():
    st.title("Página de Tips (en construcción)")


# --- 3. LÓGICA DE NAVEGACIÓN (EL CEREBRO DE LA APP) ---
if not st.session_state.logged_in:
    show_login_page()
else:
    selected = option_menu(
        menu_title=f"Hola, {st.session_state.current_user}",
        options=["PANEL", "FACTURAS", "ELECTRODOMÉSTICOS", "TIPS", "Cerrar Sesión"],
        icons=["house", "receipt", "plug", "lightbulb", "box-arrow-right"],
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#121212"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#272727"},
            "nav-link-selected": {"background-color": "#2E7D32"},
        }
    )

    if selected == "PANEL":
        show_panel_page()
    elif selected == "FACTURAS":
        show_facturas_page()
    elif selected == "ELECTRODOMÉSTICOS":
        show_electrodomesticos_page()
    elif selected == "TIPS":
        show_tips_page()
    elif selected == "Cerrar Sesión":
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.appliances = []
        st.session_state.page = 'login'
        st.rerun()
