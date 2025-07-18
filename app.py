import streamlit as st
from streamlit_option_menu import option_menu
import data_manager as dm # Importamos nuestro módulo de datos

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTADO ---
st.set_page_config(page_title="GreenCalc", page_icon="♻️", layout="centered")

# Carga eficiente de CSS usando cache_resource para que no se recargue en cada script run.
@st.cache_resource
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css('style.css')

# Inicialización del estado de la sesión (se ejecuta solo una vez por sesión de usuario).
# Este es el corazón de la persistencia de datos en el frontend.
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    # Cargamos los electrodomésticos una vez y los guardamos en la sesión para un acceso rápido.
    st.session_state.appliances = dm.load_appliances()

# --- 2. DEFINICIÓN DE PÁGINAS (Placeholders para ser llenados) ---
# Responsable: Desarrollador A (UI) y B (Lógica) colaboran en cada una.

def show_login_page():
    st.title("Bienvenido a GreenCalc ♻️")
    st.markdown("Tu asistente para un futuro más sostenible.")

    col1, col2 = st.columns(2)

    with col1:
        with st.form("login_form"):
            st.header("Iniciar Sesión")
            email = st.text_input("Correo Electrónico (simulado)")
            password = st.text_input("Contraseña (simulada)", type="password")
            submitted = st.form_submit_button("Ingresar")

            if submitted:
                if email and password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = email.split('@')[0].capitalize()
                    st.experimental_rerun()
                else:
                    st.error("Por favor, completa ambos campos.")

    with col2:
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
                    st.experimental_rerun()
                else:
                    st.error("Por favor, completa todos los campos.")

def show_panel_page():
    st.title(f"Panel de Control, {st.session_state.current_user}! 📈")

    df_records = dm.load_records()
    appliances = st.session_state.appliances

    # Realizar cálculos una sola vez
    avg_consumo = df_records["Consumo (kWh)"].mean() if not df_records.empty else 0
    consumo_electrodomesticos = sum(
        (a['potencia'] * a['cantidad'] * a['horas_dia'] * a['dias_semana'] * 4) / 1000 for a in appliances
    )
    total_estimado = consumo_electrodomesticos + avg_consumo

    # Mostrar KPIs en un layout claro
    st.subheader("Resumen Mensual")
    col1, col2, col3 = st.columns(3)
    col1.metric("Consumo Total Estimado", f"{total_estimado:.2f} kWh/mes")
    col2.metric("Consumo Facturas (Prom.)", f"{avg_consumo:.2f} kWh")
    col3.metric("Consumo Electrodomésticos", f"{consumo_electrodomesticos:.2f} kWh")

    # Visualización simple y eficiente
    if appliances:
        st.subheader("Distribución de Consumo por Electrodoméstico")
        app_consumo_df = pd.DataFrame([{
            'Electrodoméstico': a['tipo'],
            'Consumo kWh': (a['potencia'] * a['cantidad'] * a['horas_dia'] * a['dias_semana'] * 4) / 1000
        } for a in appliances])

        app_consumo_df = app_consumo_df.groupby('Electrodoméstico')['Consumo kWh'].sum()
        st.bar_chart(app_consumo_df)

def show_facturas_page():
    st.title("Gestión de Facturas 🧾")
    st.markdown("Registra tus facturas para un seguimiento preciso.")

    with st.form("factura_form"):
        st.subheader("Agregar dato factura")
        col1, col2 = st.columns(2)
        consumo_kwh = col1.number_input("Consumo (kWh)", min_value=0.0, format="%.2f")
        costo_ars = col2.number_input("Costo Consumo (ARS)", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Guardar Registro")
        if submitted and consumo_kwh > 0:
            dm.save_record(consumo_kwh, costo_ars)
            st.success("¡Factura registrada con éxito!")

    st.subheader("Registro de Consumos Pasados")
    df_records = dm.load_records()
    st.dataframe(df_records, use_container_width=True)

    if not df_records.empty:
        avg_consumo = df_records["Consumo (kWh)"].mean()
        st.metric(label="Tu Consumo Promedio Mensual (Facturas)", value=f"{avg_consumo:.2f} kWh")

    st.info("**Dato de contexto:** El consumo promedio en Chaco es de 250 kWh. ¡Compara y busca mejorar!")

def show_electrodomesticos_page():
    st.title("Mis Electrodomésticos 🔌")

    # Base de datos de potencias (fuente: Consumo Total Actualizado.docx)
    appliance_db = {
        "Heladera c/freezer": {"potencia": 150}, "Aire Acond. Split 2200fg": {"potencia": 877.5},
        "Lavadora Automática": {"potencia": 500}, "Horno eléctrico 30L": {"potencia": 1500},
        "Lámpara LED 11W": {"potencia": 11}, "CPU de escritorio": {"potencia": 200},
        "Laptop/Notebook": {"potencia": 60}, "Pava eléctrica": {"potencia": 2000},
        "Cargador de celular": {"potencia": 5}, "Router WiFi": {"potencia": 10}
    }

    with st.form("appliance_form", clear_on_submit=True):
        st.subheader("Añadir nuevo")
        col1, col2, col3, col4 = st.columns(4)
        tipo = col1.selectbox("Tipo", options=list(appliance_db.keys()))
        horas = col2.number_input("Horas/día", min_value=0.1, value=1.0, step=0.5)
        dias = col3.number_input("Días/semana", min_value=1, max_value=7, value=7)
        cantidad = col4.number_input("Cantidad", min_value=1, value=1)

        submitted = st.form_submit_button("Añadir")
        if submitted:
            new_appliance = {
                "tipo": tipo, "horas_dia": horas, "dias_semana": dias, "cantidad": cantidad,
                "potencia": appliance_db[tipo]["potencia"]
            }
            dm.save_appliance(new_appliance)
            st.session_state.appliances.append(new_appliance)
            st.success(f"¡{tipo} añadido!")

    st.subheader("Lista de Electrodomésticos")
    if not st.session_state.appliances:
        st.warning("Aún no has añadido ningún electrodoméstico.")
    else:
        cols = st.columns(3)
        for i, appliance in enumerate(st.session_state.appliances):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{appliance['cantidad']}x {appliance['tipo']}**")
                    with st.expander("Ver detalles"):
                        # Cálculos que solo se ejecutan al hacer clic (Lazy Loading)
                        potencia_total = appliance['potencia'] * appliance['cantidad']
                        consumo_mensual = (potencia_total * appliance['horas_dia'] * appliance['dias_semana'] * 4) / 1000
                        st.metric(label="Consumo Mensual Est.", value=f"{consumo_mensual:.2f} kWh")
                        st.caption(f"Uso: {appliance['horas_dia']}h/día, {appliance['dias_semana']} días/sem.")

def show_tips_page():
    st.title("Consejos para un Hogar Sostenible 🌱")
    st.markdown("Pequeños cambios, gran impacto. Aquí tienes algunas ideas:")

    tips = {
        "💡 Iluminación Eficiente": "Reemplaza tus bombillas por tecnología LED. Consumen hasta un 85% menos y duran más. ¡Apaga siempre las luces al salir de una habitación!",
        "🔌 'Consumo Fantasma'": "Desenchufa aparatos que no uses. Muchos consumen energía en standby. Usa zapatillas con interruptor.",
        "❄️ Aire Acondicionado a 24°C": "En verano, fija la temperatura en 24°C. Cada grado menos aumenta el consumo en un 8%. Limpia los filtros regularmente.",
        "💧 Lavar con Agua Fría": "La mayor parte de la energía de un lavarropas se usa para calentar el agua. Lavar en frío es igual de efectivo y ahorra muchísimo.",
        "💻 Optimiza tu PC": "Configura el modo de suspensión tras 15 minutos de inactividad. Apágala por completo si no la usarás por varias horas."
    }

    for tip_title, tip_content in tips.items():
        with st.expander(tip_title):
            st.write(tip_content)


# --- 3. LÓGICA DE NAVEGACIÓN (EL CEREBRO DE LA APP) ---
# Responsable: Desarrollador B (Lógica)

if not st.session_state.logged_in:
    # Si el usuario no está logueado, solo mostramos la página de login.
    show_login_page()
else:
    # Si está logueado, mostramos la barra de navegación y la página seleccionada.
    # Responsable: Desarrollador A (UI)
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

    # Enrutador principal: simple y eficiente. Llama solo a la función necesaria.
    if selected == "PANEL":
        show_panel_page()
    elif selected == "FACTURAS":
        show_facturas_page()
    elif selected == "ELECTRODOMÉSTICOS":
        show_electrodomesticos_page()
    elif selected == "TIPS":
        show_tips_page()
    elif selected == "Cerrar Sesión":
        # Limpiamos el estado de la sesión y forzamos una recarga para volver al login.
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.appliances = [] # Limpiar también los datos del usuario
        st.experimental_rerun()
