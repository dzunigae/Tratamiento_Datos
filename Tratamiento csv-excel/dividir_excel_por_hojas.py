# Este script recorre una carpeta de entrada en busca de archivos Excel (.xlsx)
# y procesa cada uno de ellos según la cantidad de hojas que contengan.
#
# Si un archivo tiene una sola hoja, se copia íntegramente a la carpeta de salida.
# Si tiene múltiples hojas, cada hoja se extrae y se guarda como un archivo
# Excel independiente, usando el nombre del archivo original y el de la hoja.
#
# El script valida la existencia de la carpeta de entrada, crea la carpeta de
# salida si no existe y maneja errores de carga o lectura de archivos y hojas.

import pandas as pd
import os

# Rutas de las carpetas
input_folder = './10. Dividir archivo excels en las hojas que tenga/assets'
output_folder = './10. Dividir archivo excels en las hojas que tenga/out'

# Obtener la lista de archivos en la carpeta de entrada
try:
    input_files = os.listdir(input_folder)
except FileNotFoundError:
    raise FileNotFoundError(f"La carpeta de entrada '{input_folder}' no existe.")

# Filtrar solo archivos de Excel
excel_files = [file for file in input_files if file.endswith('.xlsx')]

# Asegurarse de que haya al menos un archivo de Excel
if not excel_files:
    raise FileNotFoundError("No se encontraron archivos de Excel en la carpeta 'assets'.")

# Asegúrate de que la carpeta de salida exista
os.makedirs(output_folder, exist_ok=True)

# Procesar cada archivo de Excel
for excel_file in excel_files:
    excel_path = os.path.join(input_folder, excel_file)
    
    # Cargar el archivo de Excel
    try:
        xls = pd.ExcelFile(excel_path)
    except Exception as e:
        print(f"No se pudo cargar el archivo '{excel_file}'. Error: {e}")
        continue

    # Verificar el número de hojas
    sheet_names = xls.sheet_names
    if len(sheet_names) == 1:
        # Copiar el archivo completo si tiene solo una hoja
        output_file = os.path.join(output_folder, excel_file)
        try:
            df = pd.read_excel(excel_path)
            df.to_excel(output_file, index=False)
            print(f'Archivo "{excel_file}" copiado a la carpeta de salida.')
        except Exception as e:
            print(f"No se pudo copiar el archivo '{excel_file}'. Error: {e}")
    else:
        # Iterar sobre cada hoja y guardarla como un nuevo archivo
        for sheet_name in sheet_names:
            try:
                # Leer la hoja
                df = pd.read_excel(xls, sheet_name=sheet_name)
                
                # Guardar la hoja en un nuevo archivo Excel en la carpeta de salida
                output_file = os.path.join(output_folder, f'{os.path.splitext(excel_file)[0]}_{sheet_name}.xlsx')
                df.to_excel(output_file, index=False)

                print(f'Hoja "{sheet_name}" del archivo "{excel_file}" guardada en el archivo "{output_file}".')
            except Exception as e:
                print(f"No se pudo procesar la hoja '{sheet_name}' del archivo '{excel_file}'. Error: {e}")
