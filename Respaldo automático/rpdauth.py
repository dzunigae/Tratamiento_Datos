# Importación de herramientas comunes
import sys
import os
sys.path.append(os.path.abspath("."))
# Resto de importaciones
import shutil
import hashlib
from datetime import datetime
from herramientas_comunes import encontrar_assets, enable_privileges

def get_file_size(path):
    return os.path.getsize(path) if os.path.exists(path) else -1

def get_mod_time(path):
    return os.path.getmtime(path) if os.path.exists(path) else -1

def calculate_hash(path, algorithm='sha256', chunk_size=8192):
    try:
        hash_func = hashlib.new(algorithm)
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        return None

def compare_files(src, dst):
    details = {
        "src": src,
        "dst": dst,
        "exists_dst": os.path.exists(dst),
        "size_src": get_file_size(src),
        "size_dst": get_file_size(dst) if os.path.exists(dst) else -1,
        "mod_src": get_mod_time(src),
        "mod_dst": get_mod_time(dst) if os.path.exists(dst) else -1,
        "hash_src": None,
        "hash_dst": None,
        "hash_different": False,
        "reason": "",
    }

    if not details["exists_dst"]:
        details["reason"] = "No existía"
        return True, details

    if details["size_src"] != details["size_dst"]:
        details["reason"] = "Tamaño diferente"
        return True, details

    if int(details["mod_src"]) != int(details["mod_dst"]):
        details["reason"] = "Fecha diferente"
        return True, details

    details["hash_src"] = calculate_hash(src)
    details["hash_dst"] = calculate_hash(dst)

    if details["hash_src"] != details["hash_dst"]:
        details["reason"] = "Hash diferente"
        details["hash_different"] = True
        return True, details

    return False, details

def copy_file(source, target, changes, details=None):
    try:
        shutil.copy2(source, target)
        if details:
            if not details["exists_dst"]:
                changes.append(f"Añadido: {target}")
            else:
                changes.append(f"Modificado: {target} (Razón: {details['reason']})")
        else:
            changes.append(f"Añadido o modificado: {target}")
    except Exception as e:
        changes.append(f"Error copiando {source} a {target}: {str(e)}")

def delete_path(path, changes):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
            changes.append(f"Carpeta eliminada: {path}")
        else:
            os.remove(path)
            changes.append(f"Eliminado: {path}")
    except Exception as e:
        changes.append(f"Error eliminando {path}: {str(e)}")

def report_conflict(details, conflict_dir, conflict_log, changes):
    os.makedirs(conflict_dir, exist_ok=True)
    base_name = os.path.basename(details["src"])

    src_copy = os.path.join(conflict_dir, base_name + "_src")
    dst_copy = os.path.join(conflict_dir, base_name + "_dst")

    try:
        shutil.copy2(details["src"], src_copy)
        shutil.copy2(details["dst"], dst_copy)
    except Exception as e:
        changes.append(f"Error copiando archivos en conflicto: {e}")
        print(f"Error copiando archivos en conflicto: {e}")

    with open(conflict_log, "a", encoding="utf-8") as log:
        log.write(f"\n[Conflicto detectado - {datetime.now()}]\n")
        log.write(f"Archivo         : {base_name}\n")
        log.write(f"Motivo          : {details['reason']}\n")
        log.write(f"Tamaño          : {details['size_src']} bytes\n")
        log.write(f"Origen modificado: {datetime.fromtimestamp(details['mod_src'])}\n")
        log.write(f"Backup modificado: {datetime.fromtimestamp(details['mod_dst'])}\n")
        log.write(f"Hash origen     : {details['hash_src']}\n")
        log.write(f"Hash backup     : {details['hash_dst']}\n")
        log.write(f"Copias guardadas: {src_copy}, {dst_copy}\n")
        log.write("-" * 40 + "\n")

def sync_directories(source, backup, log_file, conflict_dir=encontrar_assets("Respaldo de archivos") / "conflictos", conflict_log=encontrar_assets("Respaldo de archivos") / "conflictos" / "log_conflictos.txt"):
    changes = []

    if not os.path.exists(backup):
        os.makedirs(backup)
        changes.append(f"Directorio creado: {backup}")

    try:
        source_items = set(os.listdir(source))
        backup_items = set(os.listdir(backup))
    except Exception as e:
        changes.append(f"Error leyendo directorios: {e}")
        print(f"Error leyendo directorios: {e}")
        return

    for item in backup_items - source_items:
        delete_path(os.path.join(backup, item), changes)

    for item in source_items:
        src_path = os.path.join(source, item)
        dst_path = os.path.join(backup, item)

        if os.path.isdir(src_path):
            sync_directories(src_path, dst_path, log_file, conflict_dir, conflict_log)
        else:
            is_diff, details = compare_files(src_path, dst_path)
            if is_diff:
                if details.get("hash_different"):
                    report_conflict(details, conflict_dir, conflict_log, changes)
                copy_file(src_path, dst_path, changes, details)

    if changes:
        try:
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"\n[{datetime.now()}] Cambios en {backup}:\n")
                log.write("\n".join([f"- {c}" for c in changes]))
                log.write("\n")
        except Exception as e:
            changes.append(f"Error escribiendo el log: {e}")
            print(f"Error escribiendo el log: {e}")

    if changes:
        print(f"{len(changes)} cambios aplicados en {backup}.")
    else:
        print(f"No hubo cambios en {backup}.")

def main():
    rutas_file = encontrar_assets("Respaldo de archivos") / "rutas.txt"
    log_file = encontrar_assets("Respaldo de archivos") / "backup_log.txt"

    if not os.path.exists(rutas_file):
        print(f"Archivo '{rutas_file}' no encontrado. Crea un archivo con las rutas:")
        print("Línea 1: Ruta del directorio origen")
        print("Línea 2: Ruta del directorio respaldo")
        return

    with open(rutas_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if len(lines) < 2:
        print("El archivo de rutas debe tener exactamente 2 líneas: origen y respaldo.")
        return

    source_dir, backup_dir = lines[:2]

    print("\n=== Verificación de rutas ===")
    print(f"Directorio origen : {source_dir}")
    print(f"Directorio respaldo: {backup_dir}")
    confirm = input("\n¿Son correctas estas rutas? (s/n): ").lower()

    if confirm == "s":
        print("\nIniciando sincronización...\n")
        sync_directories(source_dir, backup_dir, log_file)
    else:
        print("Sincronización cancelada.")

if __name__ == "__main__":
    # Ejecutar para habilitar privilegios
    enable_privileges()
    main()