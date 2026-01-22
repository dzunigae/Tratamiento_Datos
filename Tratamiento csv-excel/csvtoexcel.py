import pandas as pd
import os

RUTA = './1. Tratamiento csv-excel'
ARCHIVOS_PROBLEMATICOS = []

def csv_a_excel(RUTA):
    # Listar archivos CSV en la carpeta
    ARCHIVOS_CSV = [archivo for archivo in os.listdir(RUTA+'/assets') if archivo.endswith('.csv')]
    
    # Iterar sobre los archivos CSV
    for archivo in ARCHIVOS_CSV:
        try: 
            # Construir la ruta completa de los archivos CSV
            ruta_csv = os.path.join(RUTA+'/assets', archivo)
            
            # Construir la ruta completa de los archivos Excel
            archivo_excel = os.path.join(RUTA+'/out', archivo.replace('.csv', '.xlsx'))

            # Leer datos desde el archivo CSV
            df = pd.read_csv(ruta_csv)

            # Guardar los datos en un archivo de Excel
            df.to_excel(archivo_excel, index=False)

            print(f"Archivo CSV '{ruta_csv}' convertido a Excel correctamente.")

        except Exception as e:
            print(f"Ocurrió un error inesperado: {e} en {ruta_csv}")

            ARCHIVOS_PROBLEMATICOS.append(ruta_csv)

    for i in ARCHIVOS_PROBLEMATICOS:
        print(i)

# Reemplaza "carpeta_csv" y "carpeta_excel" con las rutas de tus carpetas
csv_a_excel(RUTA)
