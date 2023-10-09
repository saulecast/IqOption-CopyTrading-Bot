import sys
from cx_Freeze import setup, Executable

# Directorio de trabajo actual
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Para aplicaciones con GUI en Windows

# Configuración del ejecutable
executables = [Executable("main.py", base=base)]

# Opciones de configuración
build_options = {
    "packages": ["iqoptionapi", "tkinter", "threading", "datetime", "idna"],
    "excludes": [],
    "include_files": ["cuenta.txt"],
}

# Crea el ejecutable
setup(
    name="IQOptionBot",
    version="1.0",
    description="IQ Option Bot",
    options={"build_exe": build_options},
    executables=executables
)
