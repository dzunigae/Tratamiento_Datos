# Importación de herramientas comunes
import sys
import os
sys.path.append(os.path.abspath("."))
# Resto de importaciones
import subprocess
import re
import ctypes
import pandas as pd
import sqlite3
import threading
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
from ctypes import wintypes
from herramientas_comunes import encontrar_assets, enable_privileges

# Configuración de rutas
BASE_DIR = encontrar_assets("Reporte de metadatos")
EXIFTOOL_PATH = encontrar_assets("*exiftool*")
DB_PATH = os.path.join(BASE_DIR, "metadata_analysis.db")
EXCEL_PATH = os.path.join(BASE_DIR, "informe_exiftool.xlsx")
MODIFIED_REPORT_PATH = os.path.join(BASE_DIR, "archivos_modificados.xlsx")

# Selección de directorio a analizar

# Oculta la ventana principal de tkinter
root = tk.Tk()
root.withdraw()

DIRECTORIO_A_ANALIZAR = filedialog.askdirectory(
    title="Seleccione el directorio del disco externo"
)

if not DIRECTORIO_A_ANALIZAR:
    raise Exception("No se seleccionó ningún directorio")

print("Directorio seleccionado:", DIRECTORIO_A_ANALIZAR)

# Variable de control para detener la ejecución
stop_execution = False

def create_stop_button():
    """Crea una ventana con un botón para detener la ejecución en cualquier momento."""
    def stop():
        global stop_execution
        stop_execution = True
        root.quit()
        root.destroy()
    
    root = tk.Tk()
    root.title("Control de Ejecución")
    root.geometry("300x100")
    btn = tk.Button(root, text="Detener Análisis", command=stop, font=("Arial", 12))
    btn.pack(expand=True)
    root.mainloop()

# Crear un hilo para el botón de detener
threading.Thread(target=create_stop_button, daemon=True).start()

# Crear/conectar a la base de datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ruta TEXT UNIQUE,
            nombre TEXT,
            tamano INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Verificar si un archivo ya fue procesado y si ha cambiado
def archivo_procesado(file_path, file_size):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT tamano FROM archivos WHERE ruta = ?", (file_path,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        return False, False  # Archivo no está en la BD
    return True, result[0] != file_size  # True si está, segundo valor indica si cambió

# Guardar archivo en la BD
def guardar_archivo(file_path, file_name, file_size):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO archivos (ruta, nombre, tamano) VALUES (?, ?, ?)", (file_path, file_name, file_size))
    conn.commit()
    conn.close()

# Inicializar conteo de metadatos y número de archivos
metadata_count = defaultdict(int)
num_archivos = 0
archivos_modificados = []

# Cargar datos previos si el archivo Excel existe
if os.path.exists(EXCEL_PATH):
    try:
        df_previo = pd.read_excel(EXCEL_PATH)
        
        # Extraer el número de archivos analizados previamente
        num_archivos_anterior = df_previo.loc[df_previo["Metadata"] == "Total de archivos analizados", "Frecuencia"].values
        if len(num_archivos_anterior) > 0:
            num_archivos = int(num_archivos_anterior[0])  # Recuperar el conteo previo
        
        # Extraer metadatos previos
        for _, row in df_previo.iterrows():
            if row["Metadata"] != "Total de archivos analizados":
                metadata_count[row["Metadata"]] += int(row["Frecuencia"])
                
        print(f"Se han recuperado {num_archivos} archivos analizados previamente.")
    except Exception as e:
        print(f"Error al leer el informe previo: {e}")

init_db()
enable_privileges()

# Recorrer archivos del disco externo
for root, _, files in os.walk(DIRECTORIO_A_ANALIZAR):
    for file in files:
        if stop_execution:
            print("Ejecución detenida por el usuario.")
            break # Salir del bucle de archivos
        
        file_path = os.path.join(root, file)
        file_size = os.path.getsize(file_path)

        procesado, modificado = archivo_procesado(file_path, file_size)
        
        if procesado and not modificado:
            continue  # Saltar archivos ya procesados sin cambios

        try:
            result = subprocess.run([EXIFTOOL_PATH / "exiftool.exe", file_path], capture_output=True, text=True, encoding="utf-8", errors='ignore')
            output = result.stdout
            
            if output:
                num_archivos += 1
                print(f'{num_archivos}. Revisando archivo: {file_path}')
                
                for line in output.splitlines():
                    match = re.match(r"^(.+?)\s+:\s+(.+)$", line)
                    if match:
                        metadata_name = match.group(1).strip()
                        metadata_count[metadata_name] += 1

                # Guardar archivo en la BD
                guardar_archivo(file_path, file, file_size)
                
                # Si el archivo estaba en la BD pero su tamaño cambió, registrarlo como modificado
                if modificado:
                    archivos_modificados.append((file, file_path, file_size))

        except Exception as e:
            print(f"Error procesando {file_path}: {e}")

    if stop_execution:
        break  # Salir del bucle de carpetas

# Crear DataFrame con resultados actualizados
df_total = pd.DataFrame([["Total de archivos analizados", num_archivos]], columns=["Metadata", "Frecuencia"])
df_metadata = pd.DataFrame(list(metadata_count.items()), columns=["Metadata", "Frecuencia"])
df_final = pd.concat([df_total, df_metadata], ignore_index=True)

# Guardar el informe actualizado
df_final.to_excel(EXCEL_PATH, index=False)
print(f"Informe actualizado generado en: {EXCEL_PATH}")

# Guardar reporte de archivos modificados
if archivos_modificados:
    df_modificados = pd.DataFrame(archivos_modificados, columns=["Nombre", "Ruta", "Nuevo Tamaño"])
    df_modificados.to_excel(MODIFIED_REPORT_PATH, index=False)
    print(f"Reporte de archivos modificados generado en: {MODIFIED_REPORT_PATH}")
