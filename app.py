import oracledb
import os
import json
import time
import stomp
from dotenv import load_dotenv

# Carga de variables de entorno
RUTA_ENTORNO = r"C:\Users\ciari\OneDrive\Desktop\Proyecto profe\config.env"
load_dotenv(dotenv_path=RUTA_ENTORNO)

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_DSN = os.getenv("DB_DSN")
CARPETA_COLA = os.getenv("CARPETA_COLA")

if not os.path.exists(CARPETA_COLA):
    os.makedirs(CARPETA_COLA)

print("Proceso de sincronización iniciado. Escuchando base de datos...")

ids_procesados = set()

while True:
    try:
        connection = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        cursor = connection.cursor()
        
        # Lectura de los registros almacenados
        cursor.execute("SELECT ID_EVENTO, TIPO_EVENTO, CONTENIDO_JSON FROM VET1 ORDER BY ID_EVENTO ASC")
        filas = cursor.fetchall()
        
        for fila in filas:
            id_evento = fila[0]
            tipo_evento = fila[1]
            contenido_json = fila[2]
            
            if id_evento not in ids_procesados:
                nombre_archivo = f"mensaje_{tipo_evento}_{id_evento}.json"
                ruta_archivo = os.path.join(CARPETA_COLA, nombre_archivo)
                
                datos = json.loads(contenido_json)
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
                
                # Generación del formato de notificación para ActiveMQ
                nombre_mascota = datos.get("mascota", "Paciente")
                diagnostico = datos.get("diagnostico", "Consulta")
                
                mensaje_chat = f"Notificación: Su mascota {nombre_mascota} ya se encuentra registrada para su atención médica (Motivo: {diagnostico})."
                
                ruta_chat = os.path.join(CARPETA_COLA, "historial_chat.txt")
                with open(ruta_chat, "a", encoding="utf-8") as ch:
                    ch.write(mensaje_chat + "\n")
                
                print(f"Registro #{id_evento} procesado y enviado a cola de mensajería externa.")
                ids_procesados.add(id_evento)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error de procesamiento: {e}")
        
    time.sleep(2)