from distutils.core import setup
import py2exe

# Nombre del ejecutable
executable_name = "IqCopyBot.exe"

# Ruta al archivo cuenta.txt
data_files = [(".", ["cuenta.txt"])]

# Dependencias adicionales desde GitHub
install_requires = ["websocket-client==0.56", 'iqoptionapi @ https://github.com/iqoptionapi/iqoptionapi/archive/refs/heads/master.zip', 'numpy==1.16.4', 'iqoptionapi'] #quizás iqoptionapi @ https://github.com/iqoptionapi/iqoptionapi/archive/refs/heads/master.zip

options = {
    "py2exe": {
        "bundle_files": 3,
        "compressed": True,
        "optimize": 2,
        "dll_excludes": ["MSVCP90.dll"],
        "packages": ['iqoptionapi', 'websocket', 'numpy'],
    }
}



# Configuración del ejecutable
console = [{
    "script": "main.py",  # Nombre de tu script principal
    "dest_base": executable_name,  # Nombre del ejecutable
}]

# Crear el ejecutable
setup(
    options=options,
    console=console,
    data_files=data_files,
    install_requires=install_requires,  # Incluir dependencias adicionales
    # dist_dir="directorio_de_salida", # El nombre que quieras
)