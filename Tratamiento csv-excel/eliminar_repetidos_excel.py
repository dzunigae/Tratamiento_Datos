import pandas as pd
import os

RUTA = './1. Tratamiento csv-excel'

def eliminar_filas_duplicadas(RUTA):
    # Listar archivos CSV en la carpeta
    ARCHIVOS_CSV = [archivo for archivo in os.listdir(RUTA+'/assets') if archivo.endswith('.xlsx')]

    for archivo in ARCHIVOS_CSV:
        try:
            # Construir la ruta completa de los archivos CSV
            ruta = os.path.join(RUTA+'/assets', archivo)

            # Construir la ruta completa de los archivos Excel
            archivo_excel = os.path.join(RUTA+'/out', archivo)

            # Leer el archivo Excel
            df = pd.read_excel(ruta, header=0)

            # Eliminar filas duplicadas
            #df_sin_duplicados = df.drop_duplicates(subset=['NOMBRE_ENTIDAD', 'ID_DE_LA_CONVOCATORIA', 'CC_ESTUDIANTE_QUE_APLICO'])
            #df_sin_duplicados = df.drop_duplicates(subset=['NAME'])
            df_sin_duplicados = df.drop_duplicates()

            # Guardar el resultado en un nuevo archivo Excel
            df_sin_duplicados.to_excel(archivo_excel, index=False)

            print("Filas duplicadas eliminadas correctamente.")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e} en {ruta}")

# Reemplaza "archivo_entrada.xlsx" y "archivo_salida.xlsx" con los nombres de tus archivos
eliminar_filas_duplicadas(RUTA)
