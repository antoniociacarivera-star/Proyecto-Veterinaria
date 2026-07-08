import streamlit as st
import os
import json
import oracledb
from dotenv import load_dotenv

# Configuración del entorno
RUTA_ENTORNO = r"C:\Users\ciari\OneDrive\Desktop\Proyecto profe\config.env"
load_dotenv(dotenv_path=RUTA_ENTORNO)

CARPETA_COLA = os.getenv("CARPETA_COLA")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_DSN = os.getenv("DB_DSN")

st.set_page_config(
    page_title="Sistema Veterinaria", 
    page_icon="🐾", 
    layout="wide"
)

def ejecutar_sql(query, params=(), fetch=False):
    try:
        connection = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        cursor = connection.cursor()
        cursor.execute(query, params)
        if fetch:
            resultado = cursor.fetchall()
        else:
            connection.commit()
            resultado = True
        cursor.close()
        connection.close()
        return resultado
    except Exception as e:
        st.sidebar.error(f"Error de conexión: {e}")
        return None

# Estilos de la interfaz
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .titulo-principal { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-principal { color: #4b5563; text-align: center; margin-bottom: 30px; font-size: 18px; }
    .card-paciente { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #3b82f6; margin-bottom: 5px; }
    .nombre-mascota { color: #1e40af; font-size: 22px; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; }
    .info-label { font-weight: bold; color: #4b5563; }
    .info-value { color: #1f2937; }
    .tag-evento { background-color: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    .burbuja-chat { 
        background-color: #1e293b; 
        color: #ffffff; 
        padding: 15px; 
        border-radius: 15px; 
        margin-bottom: 12px; 
        border-left: 5px solid #10b981; 
        font-family: sans-serif;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Menú de navegación lateral
st.sidebar.title("Menú Principal")
modulo = st.sidebar.radio("Módulo:", ["Atención Veterinaria", "Notificaciones al Cliente"])

if modulo == "Atención Veterinaria":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Acciones de Base de Datos")
    opcion = st.sidebar.selectbox("Seleccione:", ["Registrar Mascota", "Editar Mascota", "Eliminar Mascota"])

    if opcion == "Registrar Mascota":
        st.sidebar.subheader("Nueva Consulta")
        nom = st.sidebar.text_input("Nombre de la Mascota:")
        diag = st.sidebar.text_input("Diagnóstico:")
        costo = st.sidebar.number_input("Costo ($):", min_value=0, value=100)
        
        if st.sidebar.button("Guardar"):
            if nom and diag:
                json_datos = json.dumps({"mascota": nom, "diagnostico": diag, "costo": costo})
                query = "INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) VALUES ('NUEVA_CONSULTA', :1)"
                if ejecutar_sql(query, (json_datos,)):
                    st.sidebar.success(f"Registro de {nom} completado.")
            else:
                st.sidebar.warning("Complete todos los campos obligatorios.")

    elif opcion == "Editar Mascota":
        st.sidebar.subheader("Modificar Datos")
        id_editar = st.sidebar.number_input("ID del Registro:", min_value=1, step=1)
        nuevo_nom = st.sidebar.text_input("Nuevo Nombre:")
        nuevo_diag = st.sidebar.text_input("Nuevo Diagnóstico:")
        nuevo_costo = st.sidebar.number_input("Nuevo Costo:", min_value=0, value=100)
        
        if st.sidebar.button("Actualizar"):
            if nuevo_nom and nuevo_diag:
                json_datos = json.dumps({"mascota": nuevo_nom, "diagnostico": nuevo_diag, "costo": nuevo_costo})
                query = "UPDATE VET1 SET CONTENIDO_JSON = :1 WHERE ID_EVENTO = :2"
                if ejecutar_sql(query, (json_datos, id_editar)):
                    st.sidebar.success(f"Registro #{id_editar} modificado.")

    elif opcion == "Eliminar Mascota":
        st.sidebar.subheader("Eliminar Registro")
        id_eliminar = st.sidebar.number_input("ID del Registro:", min_value=1, step=1)
        if st.sidebar.button("Borrar", type="primary"):
            query = "DELETE FROM VET1 WHERE ID_EVENTO = :1"
            if ejecutar_sql(query, (id_eliminar,)):
                st.sidebar.success(f"Registro #{id_eliminar} eliminado de la base de datos.")

# Panel de administración
if modulo == "Atención Veterinaria":
    st.markdown('<h1 class="titulo-principal">Clínica Veterinaria - Panel de Control</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-principal">Control de flujo de pacientes y sala de espera</p>', unsafe_allow_html=True)

    archivos = [f for f in os.listdir(CARPETA_COLA) if f.endswith('.json')] if os.path.exists(CARPETA_COLA) else []

    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="Pacientes en Espera", value=len(archivos))
    with col2: st.success("Servidor de Base de Datos: Activo")
    with col3: st.info("Sincronización en tiempo real: Activada")

    st.markdown("<br><h3>Lista de Espera Actual</h3>", unsafe_allow_html=True)

    if archivos:
        columnas_tarjetas = st.columns(3)
        for indice, archivo in enumerate(sorted(archivos)):
            ruta_completa = os.path.join(CARPETA_COLA, archivo)
            try:
                with open(ruta_completa, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                mascota = datos.get("mascota", "Desconocido")
                diagnostico = datos.get("diagnostico", "No especificado")
                costo = datos.get("costo", 0)
                id_evento = archivo.split('_')[-1].split('.')[0]
                
                col_actual = columnas_tarjetas[indice % 3]
                with col_actual:
                    st.markdown(f"""
                        <div class="card-paciente">
                            <div class="nombre-mascota">🐾 {mascota}</div>
                            <p><span class="info-label">Motivo:</span> <span class="info-value">{diagnostico}</span></p>
                            <p><span class="info-label">Costo Total:</span> <span class="info-value" style="color: #16a34a; font-weight: bold;">${costo} MXN</span></p>
                            <span class="tag-evento">ID: {id_evento}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Atender a {mascota}", key=f"btn_{archivo}"):
                        os.remove(ruta_completa)
                        st.rerun()
            except: pass
    else:
        st.info("No hay pacientes pendientes en este momento.")

# Pantalla del cliente
else:
    st.markdown('<h1 class="titulo-principal">Historial de Notificaciones - Cliente</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-principal">Mensajes enviados a los propietarios en tiempo real</p>', unsafe_allow_html=True)
    
    st.write("### Bandeja de Entrada:")
    
    ruta_chat = os.path.join(CARPETA_COLA, "historial_chat.txt")
    if os.path.exists(ruta_chat):
        with open(ruta_chat, "r", encoding="utf-8") as ch:
            lineas = ch.readlines()
        
        for linea in reversed(lineas):
            if linea.strip():
                st.markdown(f'<div class="burbuja-chat">{linea}</div>', unsafe_allow_html=True)
        
        if st.button("Limpiar Historial"):
            os.remove(ruta_chat)
            st.rerun()
    else:
        st.info("Sin notificaciones nuevas. Registre un paciente para enviar actualizaciones.")

if st.sidebar.button("Actualizar Interfaz"):
    st.rerun()