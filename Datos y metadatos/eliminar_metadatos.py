# De momento toca proveer manualmente el csv generado por el reporte de datos y metadatos

# Importación de herramientas comunes
import sys
import os
sys.path.append(os.path.abspath("."))
import csv
import json
import subprocess
from pathlib import Path
from datetime import datetime
from herramientas_comunes import encontrar_assets, enable_privileges, seleccionar_directorio

# CONFIG
EXIFTOOL_PATH = encontrar_assets("*exiftool*")
ARCHIVOS = seleccionar_directorio()
CSV_TAGS = encontrar_assets("Eliminación de metadatos") / "informe_exiftool.csv"
LOG = encontrar_assets("Eliminación de metadatos") / "limpieza_metadatos.log"

# Leer lista de tags desde CSV
with open(CSV_TAGS, newline="", encoding="utf-8") as f:
    TAGS = [row["Metadata"] for row in csv.DictReader(f, delimiter=";")]

# Saca la metadata de cada archivo en formato JSON
def obtener_metadata(archivo):
    """Devuelve metadata como dict usando exiftool -j"""
    result = subprocess.run(
        [EXIFTOOL_PATH / "exiftool.exe", 
         "-j", 
         #"-G1", 
         #"-a", 
         str(archivo)],
        capture_output=True,
    )
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout.decode("utf-8", errors="replace"))[0]
    except (json.JSONDecodeError, IndexError):
        return {}

def limpiar_tags(archivo, tags_presentes):
    """Ejecuta exiftool solo para los tags encontrados"""
    args = [EXIFTOOL_PATH / "exiftool.exe"] + [f"-{tag}=" for tag in tags_presentes] + [
        "-overwrite_original",
        str(archivo)
    ]
    subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

enable_privileges()

# LOG
with open(LOG, "a", encoding="utf-8") as log:
    log.write(f"\n=== Limpieza iniciada {datetime.now()} ===\n")
    for nombre in os.listdir(ARCHIVOS):
        ruta = os.path.join(ARCHIVOS, nombre)
        if not os.path.isfile(ruta):
            continue
        metadata = obtener_metadata(ruta)
        encontrados = []
        for tag in TAGS:
            if tag in metadata:
                encontrados.append(tag)
        if encontrados:
            limpiar_tags(ruta, encontrados)
            log.write(f"{nombre} → Eliminados: {', '.join(encontrados)}\n")
            print(f"{nombre} → Eliminados: {', '.join(encontrados)}\n")
        else:
            log.write(f"{nombre} → Sin tags objetivo\n")
    log.write("=== Limpieza finalizada ===\n")

