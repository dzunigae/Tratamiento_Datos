import ctypes
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from ctypes import wintypes
import tkinter as tk
from tkinter import filedialog

# Activar permisos necesarios para ciertas acciones
def enable_privileges():
    SE_PRIVILEGE_ENABLED = 0x00000002
    privileges = ['SeBackupPrivilege', 'SeRestorePrivilege']

    hToken = wintypes.HANDLE()
    TOKEN_ADJUST_PRIVILEGES = 0x0020
    TOKEN_QUERY = 0x0008

    class LUID(ctypes.Structure):
        _fields_ = [("LowPart", wintypes.DWORD),
                    ("HighPart", wintypes.LONG)]

    class LUID_AND_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("Luid", LUID),
                    ("Attributes", wintypes.DWORD)]

    class TOKEN_PRIVILEGES(ctypes.Structure):
        _fields_ = [("PrivilegeCount", wintypes.DWORD),
                    ("Privileges", LUID_AND_ATTRIBUTES * len(privileges))]

    # Abrir el token del proceso actual
    ctypes.windll.advapi32.OpenProcessToken(
        ctypes.windll.kernel32.GetCurrentProcess(),
        TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY,
        ctypes.byref(hToken)
    )

    tp = TOKEN_PRIVILEGES()
    tp.PrivilegeCount = len(privileges)

    for i, name in enumerate(privileges):
        luid = LUID()
        ctypes.windll.advapi32.LookupPrivilegeValueW(None, name, ctypes.byref(luid))
        tp.Privileges[i].Luid = luid
        tp.Privileges[i].Attributes = SE_PRIVILEGE_ENABLED

    # Ajustar los privilegios del token
    ctypes.windll.advapi32.AdjustTokenPrivileges(
        hToken,
        False,
        ctypes.byref(tp),
        0,
        None,
        None
    )

# Encuentra y devuelve la ruta de una carpeta presente dentro del directorio OneDrive (Sirve sólo en Windows)
def encontrar_assets(carpeta: str) -> Path:
    base = Path.home() / "OneDrive"  # funciona en Windows moderno

    if not base.exists():
        raise RuntimeError(f"{str(base)} no está disponible en este sistema")
    
    coincidencias = []
    # 1. Bucle: recorre todo lo que coincida con el nombre
    for ruta in base.rglob(f"{carpeta}"):
        # 2. Condición: ¿Es una carpeta?
        if ruta.is_dir():
            # 3. Acción: Agrégalo a la lista
            coincidencias.append(ruta)

    # Si no hay ninguna coincidencia
    if not coincidencias:
        raise FileNotFoundError(
            f"No se encontró ninguna carpeta que contenga '{carpeta}'"
        )
    
    # Si hay varias coincidencias
    if len(coincidencias) > 1:
        # Inicializar Tk sin mostrar ventana principal
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        rutas = "\n".join(str(r) for r in coincidencias)
        messagebox.showwarning(
            title="Múltiples carpetas encontradas",
            message=(
                f"Se encontraron varias carpetas que coinciden con '{carpeta}':\n\n"
                f"{rutas}\n\n"
                "Se utilizará la primera encontrada."
            )
        )
        root.destroy()

    return coincidencias[0]

# Función para que el usuario seleccione un directorio visualmente
def seleccionar_directorio() -> str:
    # Oculta la ventana principal de tkinter
    root = tk.Tk()
    root.withdraw()

    DIRECTORIO = filedialog.askdirectory(
        title="Seleccione el directorio del disco externo"
    )

    if not DIRECTORIO:
        raise Exception("No se seleccionó ningún directorio")

    print("Directorio seleccionado:", DIRECTORIO)

    return DIRECTORIO