import streamlit as st
import sqlite3
import datetime
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Sistema Médico Quirúrgico HPAO - UNERG",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- RUTA DEL LOGO LOCAL ---
RUTA_LOGO = "logo_unerg.png"

# --- FUNCIÓN AUXILIAR PARA MOSTRAR LOGO ---
def mostrar_logo(ancho=250):
    if os.path.exists(RUTA_LOGO):
        st.image(RUTA_LOGO, width=ancho)
    else:
        st.caption("🏫 *Universidad Rómulo Gallegos*")

# --- ESTILOS CSS CON PALETA AZUL UNERG ---
st.markdown("""
    <style>
    .main { background-color: #F4F6F9; }
    .header-unerg {
        background: linear-gradient(135deg, #1F2472 0%, #004080 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }
    .card-paciente {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        border-left: 6px solid #1F2472;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #1F2472 0%, #004080 100%);
        color: #FFFFFF !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        padding: 12px 20px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #D4AF37 0%, #B89628 100%);
        color: #1F2472 !important;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS Y CONEXIÓN ---
DB_NAME = "historial_hpao.db"

def obtener_conexion():
    return sqlite3.connect(DB_NAME)

def inicializar_base_de_datos():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Usuarios (id_usuario INTEGER PRIMARY KEY AUTOINCREMENT, nombre_completo TEXT NOT NULL, usuario TEXT UNIQUE NOT NULL, password TEXT NOT NULL, rol TEXT NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS Pacientes (id_paciente INTEGER PRIMARY KEY AUTOINCREMENT, cedula TEXT UNIQUE NOT NULL, nombre TEXT NOT NULL, apellido TEXT NOT NULL, fecha_nacimiento TEXT NOT NULL, sexo TEXT NOT NULL, telefono TEXT, municipio TEXT, parroquia TEXT);")
    cursor.execute("CREATE TABLE IF NOT EXISTS Antecedentes (id_antecedente INTEGER PRIMARY KEY AUTOINCREMENT, id_paciente INTEGER UNIQUE, personales TEXT, familiares TEXT, habitos TEXT, FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente));")
    cursor.execute("CREATE TABLE IF NOT EXISTS Atenciones_HPAO (id_atencion INTEGER PRIMARY KEY AUTOINCREMENT, id_paciente INTEGER, fecha_atencion TEXT, servicio TEXT, tipo_ingreso TEXT, motivo TEXT, signos_vitales TEXT, imc TEXT, diagnostico TEXT, tratamiento TEXT, medico_tratante TEXT, FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente));")
    
    cursor.execute("SELECT COUNT(*) FROM Usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Usuarios (nombre_completo, usuario, password, rol) VALUES ('Médico UNERG', 'admin', '1234', 'Administrador')")
    
    conn.commit()
    conn.close()

inicializar_base_de_datos()

# --- PANTALLA DE LOGIN ---
def pantalla_login():
    col1, col2, col3 = st.columns([1, 2.2, 1])
    with col2:
        col_img1, col_img2, col_img3 = st.columns([1, 3, 1])
        with col_img2:
            mostrar_logo(ancho=280)
        
        st.markdown("<h2 style='text-align: center; color: #1F2472; margin-top: 10px;'>Universidad Rómulo Gallegos</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #555;'>Hospital Pablo Acosta Ortíz (HPAO)</h4>", unsafe_allow_html=True)
        st.markdown("---")

        tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrar Nuevo Usuario"])

        with tab1:
            usuario = st.text_input("Usuario / Cédula", key="log_user")
            password = st.text_input("Contraseña", type="password", key="log_pass")
            if st.button("Acceder al Sistema", use_container_width=True):
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("SELECT nombre_completo, rol FROM Usuarios WHERE usuario = ? AND password = ?", (usuario.strip(), password.strip()))
                res = cursor.fetchone()
                conn.close()

                if res:
                    st.session_state['logeado'] = True
                    st.session_state['usuario_nombre'] = res[0]
                    st.session_state['usuario_rol'] = res[1]
                    st.success(f"¡Bienvenido/a, Dr/a. {res[0]}!")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. (Usuario por defecto: admin / 1234)")

        with tab2:
            nom_reg = st.text_input("Nombre y Apellido")
            user_reg = st.text_input("Usuario / Cédula para el acceso")
            pass_reg = st.text_input("Nueva Contraseña", type="password")
            rol_reg = st.selectbox("Rol Sanitario", ["Estudiante Medicina UNERG", "Médico Residente", "Especialista / Docente", "Administrador"])
            
            if st.button("Crear Cuenta", use_container_width=True):
                if nom_reg and user_reg and pass_reg:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO Usuarios (nombre_completo, usuario, password, rol) VALUES (?, ?, ?, ?)", (nom_reg.strip(), user_reg.strip(), pass_reg.strip(), rol_reg))
                        conn.commit()
                        st.success("✅ ¡Cuenta creada exitosamente! Ve a 'Iniciar Sesión'.")
                    except sqlite3.IntegrityError:
                        st.error("⚠️ El usuario o cédula ya existe.")
                    finally:
                        conn.close()
                else:
                    st.warning("⚠️ Rellena todos los campos para continuar.")

# --- CONTROL DE SESIÓN ---
if 'logeado' not in st.session_state:
    st.session_state['logeado'] = False

if not st.session_state['logeado']:
    pantalla_login()
else:
    # --- MENÚ LATERAL ---
    with st.sidebar:
        mostrar_logo(ancho=180)
        st.markdown(f"### 👤 {st.session_state['usuario_nombre']}")
        st.caption(f"🎖️ {st.session_state['usuario_rol']}")
        
        if st.button("🔴 Cerrar Sesión", use_container_width=True):
            st.session_state['logeado'] = False
            st.rerun()

        st.markdown("---")
        opcion = st.radio("Navegación Inteligente", [
            "📊 Dashboard Estadístico",
            "➕ Registrar Paciente", 
            "📝 Nueva Atención Médica", 
            "🔍 Consultar Expediente Clínico"
        ])

    # === CABECERA PRINCIPAL ===
    st.markdown("""
        <div class="header-unerg">
            <h1 style="margin:0; font-size: 26px;">🏥 Sistema Digital de Historias Clínicas - UNERG</h1>
            <p style="margin:0; opacity: 0.85;">Hospital Pablo Acosta Ortíz (HPAO) | Decanato de Ciencias de la Salud</p>
        </div>
    """, unsafe_allow_html=True)

    # === OPCIÓN 1: DASHBOARD ESTADÍSTICO ===
    if opcion == "📊 Dashboard Estadístico":
        st.subheader("📈 Indicadores Epidemiológicos en Tiempo Real")
        
        conn = obtener_conexion()
        df_p = pd.read_sql_query("SELECT * FROM Pacientes", conn)
        df_a = pd.read_sql_query("SELECT * FROM Atenciones_HPAO", conn)
        conn.close()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Pacientes Registrados", len(df_p))
        c2.metric("Total Atenciones Médicas", len(df_a))
        c3.metric("Servicio Más Frecuentado", df_a['servicio'].mode()[0] if not df_a.empty else "N/A")

        st.markdown("---")
        if not df_p.empty and not df_a.empty:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("**Distribución por Sexo**")
                st.bar_chart(df_p['sexo'].value_counts())
            with col_g2:
                st.markdown("**Consultas por Servicio / Área**")
                st.bar_chart(df_a['servicio'].value_counts())
        else:
            st.info("ℹ️ Registra pacientes y consultas para ver las métricas automatizadas.")

    # === OPCIÓN 2: REGISTRAR PACIENTE ===
    elif opcion == "➕ Registrar Paciente":
        st.subheader("➕ Ficha de Filiación Única del Paciente")
        
        col1, col2 = st.columns(2)
        with col1:
            cedula = st.text_input("Cédula de Identidad *")
            nombre = st.text_input("Nombres Completo *")
            apellido = st.text_input("Apellidos Completo *")
            fecha_nac = st.date_input("Fecha de Nacimiento", min_value=datetime.date(1920, 1, 1), max_value=datetime.date.today())
            sexo = st.selectbox("Sexo Biológico", ["Masculino", "Femenino"])
        
        with col2:
            telefono = st.text_input("Teléfono Móvil / Contacto")
            municipio = st.text_input("Municipio", value="Roscio")
            parroquia = st.text_input("Parroquia", value="San Juan de los Morros")
            ant_personales = st.text_area("Antecedentes Personales (Alergias, Hipertensión, Diabetes...)", height=68)
            ant_familiares = st.text_area("Antecedentes Familiares", height=68)
            habitos = st.text_area("Hábitos Psicobiológicos (Fuma, Alcohol, etc.)", height=68)

        st.markdown("---")
        if st.button("💾 Guardar e Ingresar Paciente", use_container_width=True):
            if cedula.strip() and nombre.strip() and apellido.strip():
                conn = obtener_conexion()
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO Pacientes (cedula, nombre, apellido, fecha_nacimiento, sexo, telefono, municipio, parroquia) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                                   (cedula.strip(), nombre.strip(), apellido.strip(), str(fecha_nac), sexo, telefono.strip(), municipio.strip(), parroquia.strip()))
                    id_paciente_nuevo = cursor.lastrowid
                    cursor.execute("INSERT INTO Antecedentes (id_paciente, personales, familiares, habitos) VALUES (?, ?, ?, ?)", 
                                   (id_paciente_nuevo, ant_personales.strip(), ant_familiares.strip(), habitos.strip()))
                    conn.commit()
                    
                    st.balloons()
                    st.success(f"✅ ¡Paciente registrado con éxito! Código Único asignado: HPAO-{id_paciente_nuevo:05d}")
                except sqlite3.IntegrityError:
                    st.error("⚠️ La cédula ingresada ya se encuentra registrada en la base de datos.")
                finally:
                    conn.close()
            else:
                st.error("⚠️ Los campos Cédula, Nombre y Apellido son obligatorios.")

    # === OPCIÓN 3: NUEVA ATENCIÓN MÉDICA ===
    elif opcion == "📝 Nueva Atención Médica":
        st.subheader("📝 Evaluación Médica y Evolución Clínica")
        ced_buscar = st.text_input("🔍 Cédula del Paciente a Evaluar:")

        if ced_buscar:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_paciente, nombre, apellido, sexo, fecha_nacimiento FROM Pacientes WHERE cedula = ?", (ced_buscar.strip(),))
            pac = cursor.fetchone()
            conn.close()

            if pac:
                id_p, nom, ape, sexo, fnac = pac
                st.markdown(f"""
                    <div class="card-paciente">
                        <h4>👤 Paciente: <b>{nom} {ape}</b> | Cédula: <b>{ced_buscar}</b></h4>
                        <p><b>Sexo:</b> {sexo} &nbsp;|&nbsp; <b>Nacimiento:</b> {fnac}</p>
                    </div>
                """, unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    servicio = st.selectbox("Servicio Receptor", ["Emergencia Adultos", "Emergencia Pediátrica", "Consultorio Externo", "Hospitalización", "Traumatología", "Cirugía General"])
                    tipo_ingreso = st.selectbox("Tipo de Ingreso", ["Ambulatorio", "Emergencia", "Referido Interhospitalario"])
                    motivo = st.text_area("Motivo de Consulta y Enfermedad Actual")
                
                with col_b:
                    st.markdown("**Calculadora Integrada de IMC**")
                    col_peso, col_talla = st.columns(2)
                    peso = col_peso.number_input("Peso (kg)", min_value=1.0, max_value=250.0, value=70.0)
                    talla = col_talla.number_input("Talla (Metros)", min_value=0.5, max_value=2.3, value=1.70)
                    
                    imc_val = round(peso / (talla ** 2), 2)
                    diag_imc = "Normal"
                    if imc_val < 18.5: diag_imc = "Bajo Peso"
                    elif 25 <= imc_val < 30: diag_imc = "Sobrepeso"
                    elif imc_val >= 30: diag_imc = "Obesidad"
                    
                    st.info(f"📊 **IMC Calculado:** {imc_val} kg/m² ({diag_imc})")
                    signos = st.text_input("Otros Signos Vitales", value="TA: 120/80 mmHg | FC: 75 bpm | Temp: 36.5°C")
                    diagnostico = st.text_area("Impresión Diagnóstica")
                    tratamiento = st.text_area("Plan Terapéutico e Indicaciones")

                if st.button("💾 Registrar Atención Clínica", use_container_width=True):
                    if motivo.strip() and diagnostico.strip():
                        conn = obtener_conexion()
                        cursor = conn.cursor()
                        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        imc_final = f"{imc_val} kg/m² ({diag_imc})"
                        
                        cursor.execute("INSERT INTO Atenciones_HPAO (id_paciente, fecha_atencion, servicio, tipo_ingreso, motivo, signos_vitales, imc, diagnostico, tratamiento, medico_tratante) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                       (id_p, fecha_actual, servicio, tipo_ingreso, motivo.strip(), signos.strip(), imc_final, diagnostico.strip(), tratamiento.strip(), st.session_state['usuario_nombre']))
                        conn.commit()
                        conn.close()
                        st.balloons()
                        st.success("✅ Evolución grabada en la historia clínica del paciente correctamente.")
                    else:
                        st.warning("⚠️ Debes rellenar el Motivo de Consulta y el Diagnóstico.")
            else:
                st.error("❌ Paciente no registrado. Ve primero a 'Registrar Paciente'.")

    # === OPCIÓN 4: EXPEDIENTE CLÍNICO DIGITAL ===
    elif opcion == "🔍 Consultar Expediente Clínico":
        st.subheader("🔍 Expediente Clínico Digitalizado")
        ced_exp = st.text_input("Cédula del Paciente:")

        if ced_exp:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Pacientes WHERE cedula = ?", (ced_exp.strip(),))
            paciente = cursor.fetchone()

            if paciente:
                id_p, ci, nom, ape, fnac, sexo, tlf, mun, parr = paciente

                st.markdown(f"""
                    <div class="card-paciente">
                        <h3>📄 Expediente Médico N° HPAO-{id_p:05d}</h3>
                        <p><b>Paciente:</b> {nom} {ape} | <b>Cédula:</b> {ci} | <b>Sexo:</b> {sexo}</p>
                        <p><b>Nacimiento:</b> {fnac} | <b>Contacto:</b> {tlf} | <b>Ubicación:</b> {parr}, Mpio. {mun}</p>
                    </div>
                """, unsafe_allow_html=True)

                cursor.execute("SELECT personales, familiares, habitos FROM Antecedentes WHERE id_paciente = ?", (id_p,))
                ant = cursor.fetchone()
                if ant:
                    with st.expander("🩺 Antecedentes Médicos"):
                        st.write(f"**Personales:** {ant[0]}")
                        st.write(f"**Familiares:** {ant[1]}")
                        st.write(f"**Hábitos:** {ant[2]}")

                cursor.execute("SELECT fecha_atencion, servicio, tipo_ingreso, motivo, signos_vitales, imc, diagnostico, tratamiento, medico_tratante FROM Atenciones_HPAO WHERE id_paciente = ? ORDER BY id_atencion DESC", (id_p,))
                atenciones = cursor.fetchall()
                conn.close()

                st.markdown(f"#### 📋 Consultas e Historial Clínico ({len(atenciones)})")
                if atenciones:
                    for a in atenciones:
                        with st.expander(f"📅 {a[0]} - Servicio: {a[1]} (Atendido por: {a[8]})"):
                            st.write(f"**Tipo de Ingreso:** {a[2]}")
                            st.write(f"**Motivo de Consulta:** {a[3]}")
                            st.write(f"**Signos Vitales:** {a[4]} | **IMC:** {a[5]}")
                            st.write(f"**Diagnóstico:** {a[6]}")
                            st.write(f"**Plan Indicado:** {a[7]}")
                else:
                    st.info("ℹ️ Este paciente no registra consultas anteriores.")
            else:
                conn.close()
                st.error("❌ No se encontró ningún paciente con esa cédula.")