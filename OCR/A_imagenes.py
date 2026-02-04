# Importación de herramientas comunes
import sys
import os
sys.path.append(os.path.abspath("."))
import pytesseract
from PIL import Image
from pathlib import Path
from herramientas_comunes import seleccionar_directorio

# --- CONFIGURACIÓN ---
EXTENSION_SALIDA = input("Extensión deseada para el archivo de texto de salida:")
CARPETA_IMAGENES = Path(seleccionar_directorio())
ARCHIVO_SALIDA = f"./output/output.{EXTENSION_SALIDA}"

# OCR optimizado para leer líneas estructuradas, no dispersas por la imagen (Ideal para código)
# --psm 11 -> Busca donde sea sin estructura definida
TESS_CONFIG = r'--oem 3 --psm 6'

# Idiomas (inglés suele ayudar mucho para código)
IDIOMAS = "eng+spa"

os.makedirs("./output", exist_ok=True)

with open(ARCHIVO_SALIDA, "a", encoding="utf-8") as salida:
    salida.write("\n\n// ===== BLOQUE OCR NUEVO =====\n\n")

    for imagen in sorted(CARPETA_IMAGENES.glob("*")):
        if imagen.suffix.lower() not in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]:
            continue

        print(f"[+] Procesando {imagen.name}")

        texto = pytesseract.image_to_string(
            Image.open(imagen),
            lang=IDIOMAS,
            config=TESS_CONFIG
        )

        # Limpieza básica
        lineas = [
            linea.rstrip()
            for linea in texto.splitlines()
            if linea.strip()
        ]

        salida.write(f"\n// --- {imagen.name} ---\n")
        for linea in lineas:
            salida.write(linea + "\n")
