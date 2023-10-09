import py2exe

py2exe.freeze(
    source = "main.py", # Nombre de tu script principal
    target_name = "IqCopyBot.exe", # Nombre del ejecutable
    bundle_files = 1, # Para generar un solo archivo
    compressed = True, # Para comprimir el archivo
    data_files = [(".", ["cuenta.txt"])], # Para incluir archivos adicionales
    install_requires = ["iqoptionapi"], # Para incluir dependencias adicionales
)
