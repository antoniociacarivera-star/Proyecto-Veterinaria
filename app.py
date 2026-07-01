import tkinter as tk
from tkinter import ttk, messagebox
import oracledb

DB_USER = "SYSTEM"  
DB_PASS = "proyecto1" 
DB_DSN = "localhost:1521/xe"       

print("=" * 60)
print("INICIANDO APLICACIÓN VETERINARIA...")
print(f"Conectando directamente como: {DB_USER} al servicio: xe")
print("=" * 60)

def obtener_conexion():
    try:
        return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    except Exception as e:
        print(f"\n[❌ ERROR DE CONEXIÓN]: {e}\n")
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a Oracle:\n\n{e}")
        return None

def cargar_reporte():
    for fila in tabla.get_children():
        tabla.delete(fila)
        
    conn = obtener_conexion()
    if not conn: 
        return
    
    cursor = conn.cursor()
    
    query = """
        SELECT d.NOMBRE, m.NOMBRE_MASCOTA, m.ESPECIE, c.FECHA_CONSULTA, c.MOTIVO, c.COSTO
        FROM VET_CONSULTAS c
        JOIN VET_MASCOTAS m ON c.ID_MASCOTA = m.ID_MASCOTA
        JOIN VET_DUENOS d ON m.ID_DUENO = d.ID_DUENO
        ORDER BY c.FECHA_CONSULTA DESC
    """
    try:
        cursor.execute(query)
        for registro in cursor:
            fecha_str = registro[3].strftime('%d/%m/%Y') if registro[3] else ""
            tabla.insert("", tk.END, values=(registro[0], registro[1], registro[2], fecha_str, registro[4], f"${registro[5]:.2f}"))
        print("[OK] ¡Datos cargados con éxito desde el servicio XE!")
    except Exception as e:
        print(f"[❌ ERROR AL CONSULTAR]: {e}")
        messagebox.showerror("Error de Consulta", f"Error al traer los datos: {e}")
    finally:
        cursor.close()
        conn.close()

def registrar_consulta():
    id_mascota = entry_mascota.get()
    motivo = entry_motivo.get()
    diagnostico = entry_diag.get()
    treatment = entry_trat.get()
    costo = entry_costo.get()
    
    if not (id_mascota and motivo and costo):
        messagebox.showwarning("Campos obligatorios", "Por favor llena los campos principales:\n- ID Mascota\n- Motivo\n- Costo")
        return

    conn = obtener_conexion()
    if not conn: 
        return
    
    cursor = conn.cursor()
    try:
        print(f"[PROCESO] Llamando a PRC_REGISTRAR_CONSULTA...")
        cursor.callproc("PRC_REGISTRAR_CONSULTA", [
            int(id_mascota), 
            motivo, 
            diagnostico, 
            treatment, 
            float(costo), 
            "VS_CODE_SYSTEM"  
        ])
        
        messagebox.showinfo("Éxito", "¡Consulta registrada correctamente!\n\nEl registro se guardó en Oracle.")
        
        entry_mascota.delete(0, tk.END)
        entry_motivo.delete(0, tk.END)
        entry_diag.delete(0, tk.END)
        entry_trat.delete(0, tk.END)
        entry_costo.delete(0, tk.END)
        
        cargar_reporte()
        
    except Exception as e:
        print(f"[❌ ERROR PL/SQL]: {e}")
        messagebox.showerror("Error en PL/SQL", f"La base de datos rechazó la inserción:\n\n{e}")
    finally:
        cursor.close()
        conn.close()

ventana = tk.Tk()
ventana.title("Sistema Clínico Veterinario - Módulo de Eventos")
ventana.geometry("850x570")
ventana.configure(bg="#f4f6f9")

lbl_titulo = tk.Label(ventana, text="Clínica Veterinaria - Control de Consultas", font=("Arial", 16, "bold"), bg="#f4f6f9", fg="#2c3e50")
lbl_titulo.pack(pady=15)

frame_form = tk.LabelFrame(ventana, text=" Registrar Nueva Consulta Médica ", font=("Arial", 10, "bold"), bg="#f4f6f9", pady=10, padx=10)
frame_form.pack(fill="x", padx=20, pady=5)

tk.Label(frame_form, text="ID Mascota *:", font=("Arial", 9, "bold"), bg="#f4f6f9").grid(row=0, column=0, sticky="w", padx=5, pady=4)
entry_mascota = tk.Entry(frame_form, width=12)
entry_mascota.grid(row=0, column=1, sticky="w", padx=5, pady=4)

tk.Label(frame_form, text="Motivo *:", font=("Arial", 9, "bold"), bg="#f4f6f9").grid(row=0, column=2, sticky="e", padx=5, pady=4)
entry_motivo = tk.Entry(frame_form, width=45)
entry_motivo.grid(row=0, column=3, sticky="w", padx=5, pady=4)

tk.Label(frame_form, text="Diagnóstico:", bg="#f4f6f9").grid(row=1, column=0, sticky="w", padx=5, pady=4)
entry_diag = tk.Entry(frame_form, width=25)
entry_diag.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=4)

tk.Label(frame_form, text="Tratamiento:", bg="#f4f6f9").grid(row=1, column=2, sticky="e", padx=5, pady=4)
entry_trat = tk.Entry(frame_form, width=35)
entry_trat.grid(row=1, column=3, sticky="ew", padx=5, pady=4)

tk.Label(frame_form, text="Costo ($) *:", font=("Arial", 9, "bold"), bg="#f4f6f9").grid(row=2, column=0, sticky="w", padx=5, pady=4)
entry_costo = tk.Entry(frame_form, width=12)
entry_costo.grid(row=2, column=1, sticky="w", padx=5, pady=4)

btn_guardar = tk.Button(frame_form, text="Guardar Consulta 💾", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), padx=10, command=registrar_consulta)
btn_guardar.grid(row=2, column=3, sticky="e", padx=5, pady=4)

frame_tabla = tk.LabelFrame(ventana, text=" Historial de Consultas Realizadas (Desde Oracle) ", font=("Arial", 10, "bold"), bg="#f4f6f9", pady=10, padx=10)
frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

columnas = ("Dueño", "Mascota", "Especie", "Fecha", "Motivo", "Costo")
tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=100, anchor="center")
tabla.column("Motivo", width=220, anchor="w")

tabla.pack(fill="both", expand=True, side="left")

scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
scroll.pack(fill="y", side="right")
tabla.configure(yscrollcommand=scroll.set)

cargar_reporte()

ventana.mainloop()