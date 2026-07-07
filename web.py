import streamlit as st
import os
import json
import time
from dotenv import load_dotenv

# Buscamos el archivo con su nombre corregido
RUTA_ENTORNO = r"C:\Users\ciari\OneDrive\Desktop\Yventz\config.env"
load_dotenv(dotenv_path=RUTA_ENTORNO)

CARPETA_COLA = os.getenv("CARPETA_COLA")

# El resto de tu código de Streamlit sigue exactamente igual...

# Configuración estética de la página
st.set_page_config(
    page_title="PetOutbox - Broker Visual", 
    page_icon="🏥", 
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .titulo-principal { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-principal { color: #4b5563; text-align: center; margin-bottom: 30px; font-size: 18px; }
    .card-paciente { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #3b82f6; margin-bottom: 15px; }
    .nombre-mascota { color: #1e40af; font-size: 22px; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; }
    .info-label { font-weight: bold; color: #4b5563; }
    .info-value { color: #1f2937; }
    .tag-evento { background-color: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Encabezado bonito de inicio
st.markdown('<h1 class="titulo-principal">🏥 Sistema de Control Intermedio - PetOutbox</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-principal">Panel de mensajería asíncrona en tiempo real para la Veterinaria</p>', unsafe_allow_html=True)

# Leer archivos JSON de la carpeta
if os.path.exists(CARPETA_COLA):
    archivos = [f for f in os.listdir(CARPETA_COLA) if f.endswith('.json')]
else:
    archivos = []

# Indicadores/Métricas superiores estilizadas
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🔄 Mensajes en Cola Pendientes", value=len(archivos))
with col2:
    st.success("🟢 Relevo (Python Outbox): Conectado a Oracle")
with col3:
    st.info("⚡ Canal Visual: Modo Escucha Activo")

st.markdown("<br><h3>📋 Cola de Eventos de Pacientes</h3>", unsafe_allow_html=True)

if archivos:
    # Crear cuadrícula de 3 columnas
    columnas_tarjetas = st.columns(3)
    
    for indice, archivo in enumerate(sorted(archivos)):
        ruta_completa = os.path.join(CARPETA_COLA, archivo)
        try:
            with open(ruta_completa, "r", encoding="utf-8") as f:
                datos = json.load(f)
            
            mascota = datos.get("mascota", "Desconocido")
            diagnostico = datos.get("diagnostico", "No especificado")
            costo = datos.get("costo", 0)
            
            col_actual = columnas_tarjetas[indice % 3]
            
            with col_actual:
                st.markdown(f"""
                    <div class="card-paciente">
                        <div class="nombre-mascota">🐾 {mascota}</div>
                        <p><span class="info-label">Motivo:</span> <span class="info-value">{diagnostico}</span></p>
                        <p><span class="info-label">Total a Pagar:</span> <span class="info-value" style="color: #16a34a; font-weight: bold;">${costo} MXN</span></p>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
                            <span class="tag-evento">ID Evento: #{archivo.split('_')[-1].split('.')[0]}</span>
                            <span style="font-size: 11px; color: #9ca3af;">📦 Formato: JSON String</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        except Exception:
            pass
else:
    st.markdown("""
        <div style="background-color: #f3f4f6; border-radius: 8px; padding: 40px; text-align: center; border: 2px dashed #d1d5db; margin-top: 20px;">
            <span style="font-size: 40px;">💤</span>
            <h4 style="color: #6b7280; margin-top: 10px;">Cola de transmisión despejada</h4>
            <p style="color: #9ca3af; font-size: 14px;">Todos los eventos de la veterinaria fueron procesados con éxito por el patrón Outbox.</p>
        </div>
    """, unsafe_allow_html=True)

# El truco limpio: duerme 2 segundos y le ordena a la página recargarse sola sin romper hilos
time.sleep(2)
st.rerun()