from pyiqoptionapi import IQOption
import time

# Iniciar sesión con tu email y contraseña
API = IQOption("uncastilloteorico@gmail.com", "Esesan:29a8D8Xv")

# Esperar a que se conecte
API.connect()

# Comprobar si está conectado
while True:
    if API.check_connect() == False:
        print("Error al conectar")
        API.connect()
    else:
        print("Conectado exitosamente")
        break
    time.sleep(1)

# Establecer una compra de USD/CAD por 10 dólares, al alza, por 1 minuto
id = API.buy(10, "USD/CAD", "call", 1)

# Verificar el resultado de la compra
print("control 1")
if id != None:
    print("control 2")
    print(API.check_win_v3(id))
    print("control 3")
else:
    print("Error al comprar")

print("programa terminado")