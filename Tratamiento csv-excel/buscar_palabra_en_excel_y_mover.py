# Este script recorre una carpeta de entrada y analiza archivos Excel (.xlsx)
# para determinar si contienen una palabra clave específica en cualquiera
# de sus celdas.
#
# El contenido de cada archivo se normaliza (minúsculas y sin tildes) para
# realizar una búsqueda insensible a mayúsculas y acentos.
#
# Si el archivo contiene la palabra clave, se mueve automáticamente a una
# carpeta de salida. El script valida la existencia de carpetas y maneja
# errores de lectura y movimiento de archivos.

import pandas as pd
import os
import shutil

# Rutas de las carpetas
input_folder = './11. Filtrar archivos de excel por palabra/assets'
output_folder = './11. Filtrar archivos de excel por palabra/out'

# Crear la carpeta de salida si no existe
os.makedirs(output_folder, exist_ok=True)

# Palabra a buscar
keyword = 'nutricion'

# Obtener la lista de archivos en la carpeta de entrada
try:
    input_files = os.listdir(input_folder)
except FileNotFoundError:
    raise FileNotFoundError(f"La carpeta de entrada '{input_folder}' no existe.")

# Filtrar solo archivos de Excel
excel_files = [file for file in input_files if file.endswith('.xlsx')]

# Asegurarse de que haya al menos un archivo de Excel
if not excel_files:
    raise FileNotFoundError("No se encontraron archivos de Excel en la carpeta 'out'.")

# Función para normalizar texto
def normalize_text(text):
    return text.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

# Procesar cada archivo de Excel
for excel_file in excel_files:
    excel_path = os.path.join(input_folder, excel_file)
    
    # Cargar el archivo de Excel
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"No se pudo cargar el archivo '{excel_file}'. Error: {e}")
        continue

    # Convertir todo el DataFrame a texto y buscar la palabra clave
    contains_keyword = df.apply(lambda row: row.astype(str).apply(normalize_text).str.contains(normalize_text(keyword), regex=False).any(), axis=1).any()

    if contains_keyword:
        # Mover el archivo a la carpeta de salida
        try:
            shutil.move(excel_path, os.path.join(output_folder, excel_file))
            print(f'Archivo "{excel_file}" movido a la carpeta de salida.')
        except Exception as e:
            print(f"No se pudo mover el archivo '{excel_file}'. Error: {e}")
