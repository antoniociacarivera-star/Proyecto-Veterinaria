import oracledb
import time
import os
from dotenv import load_dotenv

# Buscamos el archivo con su nombre corregido
RUTA_ENTORNO = r"C:\Users\ciari\OneDrive\Desktop\Yventz\config.env"
load_dotenv(dotenv_path=RUTA_ENTORNO)

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_DSN = os.getenv("DB_DSN")
CARPETA_COLA = os.getenv("CARPETA_COLA")

print("=" * 60)
print("SISTEMA OUTBOX ACTIVO - ENVIANDO MENSAJES A COLA LOCAL")
print("=" * 60)

# El resto de tu código hacia abajo sigue exactamente igual...

def guardar_en_cola_local(id_evento, payload):
    try:
        nombre_archivo = f"mensaje_vet1_{id_evento}.json"
        ruta_completa = os.path.join(CARPETA_COLA, nombre_archivo)
        
        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write(payload)
            
        print(f"    [💾] Mensaje exportado con éxito a la cola: {nombre_archivo}")
        return True
    except Exception as e:
        print(f"[❌ Error al escribir el archivo]: {e}")
        return False

def revisar_tabla_outbox():
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        cursor = conn.cursor()
        
        cursor.execute("SELECT ID_EVENTO, CONTENIDO_JSON FROM VET1 ORDER BY ID_EVENTO ASC")
        eventos = cursor.fetchall()
        
        if eventos:
            print(f"\n[📦] ¡Se detectaron {len(eventos)} mensajes nuevos en VET1!")
            
            for id_evento, contenido_json in eventos:
                payload = contenido_json.read() if hasattr(contenido_json, 'read') else str(contenido_json)
                print(f" -> Despachando Evento ID {id_evento}...")
                
                if guardar_en_cola_local(id_evento, payload):
                    cursor.execute("DELETE FROM VET1 WHERE ID_EVENTO = :1", [id_evento])
                    print(f"    [✔️] Evento {id_evento} eliminado de la base de datos.")
            
            conn.commit()
        else:
            print("[💤] No hay datos nuevos en la tabla VET1. Reintentando en 3 segundos...")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[❌ Error de Oracle]: {e}")

while True:
    revisar_tabla_outbox()
    time.sleep(3)