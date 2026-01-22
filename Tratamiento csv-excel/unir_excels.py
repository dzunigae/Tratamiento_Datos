import pandas as pd

def unir_tres_excels(archivo1, archivo2,archivo_salida):
    # Leer los tres archivos Excel
    df1 = pd.read_excel(archivo1, header=1)
    df2 = pd.read_excel(archivo2, header=1)

    # Concatenar los DataFrames
    df_concatenado = pd.concat([df1, df2], ignore_index=True)

    # Guardar el resultado en un nuevo archivo Excel
    df_concatenado.to_excel(archivo_salida, index=False)

    print("Los archivos Excel se han unido correctamente.")

# Reemplaza los nombres de los archivos con los nombres de tus archivos
unir_tres_excels("nombre1.xlsx", "nombre2.xlsx", "nombre3.xlsx")
