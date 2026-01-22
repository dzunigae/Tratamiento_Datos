# Este script lee un archivo Excel y analiza una columna cuyos valores contienen
# listas de elementos separadas por comas. Para cada elemento, calcula cuántas
# veces aparece en todas las filas (frecuencia / moda).
# 
# Los resultados se ordenan de mayor a menor frecuencia mediante un algoritmo
# bubble sort personalizado y se exportan en dos formatos:
# 1) Un archivo de texto (.txt) con el conteo de cada elemento.
# 2) Un archivo Excel (.xlsx) con las columnas "Elemento" y "Frecuencia".
# 
# El nombre de la columna a analizar se solicita por consola.

import pandas as pd

data = './6. Clasificar información de celdas que contengan listas en un excel/assets/input.xlsx'
out = './6. Clasificar información de celdas que contengan listas en un excel/out/output.txt'
excel = './6. Clasificar información de celdas que contengan listas en un excel/out/output.xlsx'

def bubble_sort_tuplas(lista_de_tuplas):
    n = len(lista_de_tuplas)

    #Iteración sobre el tamaño de la lista
    for i in range(n):
        # Últimos i elementos ya están ordenados, no necesitamos compararlos
        for j in range(0, n - i - 1):
            # Comparamos los segundos elementos de las tuplas
            if lista_de_tuplas[j][1] < lista_de_tuplas[j + 1][1]:
                # Hacemos swap si el segundo elemento está en el orden incorrecto
                lista_de_tuplas[j], lista_de_tuplas[j + 1] = lista_de_tuplas[j + 1], lista_de_tuplas[j]


def moda(data,out,excel):
    #Nombre de la columna
    name = input("Nombre de la columna: ")

    #Apertura del archivo
    df_input = pd.read_excel(data,header=0)

    #Diccionario de los elementos encontrados
    things = {}
    
    #Recorrer todas las filas extrayendo la cantidad de veces que aparecen los elementos
    for i in range(len(df_input)):
        ROW = df_input.iloc[i]
        OBJECT = ROW[name]

        #Si la celda no contiene un nan
        if not pd.isna(OBJECT):
            VALORES = OBJECT.split(', ')
            #Rellenar el diccionario con la moda de los elementos
            for j in VALORES:
                if j in things:
                    things[j] = things[j] + 1
                else:
                    things[j] = 1

    #Convertir diccionario en lista de tuplas
    touples_list = list(things.items())

    #Ordenar de mayor a menor las frecuencias
    bubble_sort_tuplas(touples_list)

    #Reporte formato txt
    with open(out, 'w') as output:
        for i in range(len(touples_list)):
            output.write(touples_list[i][0]+": "+str(touples_list[i][1])+"\n")

    #Convertir el diccionario en un data frame
    keys = list(things.keys())
    values = list(things.values())

    #Reporte a excel
    df_reporte_excel = pd.DataFrame(list(zip(keys,values)), columns=['Elemento','Frecuencia'])
    df_reporte_excel.to_excel(excel,index=False)

moda(data,out,excel)