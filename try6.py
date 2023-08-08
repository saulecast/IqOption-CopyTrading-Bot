from iqoptionapi.stable_api import IQ_Option
import time

# Credenciales para las cuentas
username_origen = 'uncastilloteorico@gmail.com'
password_origen = 'Esesan:29a8D8Xv'

# Leer las credenciales de la segunda cuenta desde el archivo
def read_second_account_credentials(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        username = lines[0].strip().split(":")[1].strip()
        password_parts = lines[1].strip().split(": ")[1:]
        password = "".join(password_parts)
        print(password)
        print(username)
    return username, password_parts

# Obtener las credenciales de la segunda cuenta desde el archivo
username_destino, password_destino = read_second_account_credentials("cuenta.txt")

# Inicializar la API para ambas cuentas
api_origen = IQ_Option(username_origen, password_origen)
api_destino = IQ_Option(username_destino, password_destino)

# Conectar a las cuentas
api_origen.connect()
api_destino.connect()

# Lista para rastrear operaciones ya imitadas
imitados = []

def get_instrument_type(position):
    # Obtener el tipo de instrumento basado en la información de la posición
    if "instrument_type" in position:
        return position["instrument_type"]
    return None

def imitate_trade(active_id, amount, direction, asset_name, expiration):
    global imitados
    # Obtener el saldo actual de la segunda cuenta utilizando la API
    balance_destino = api_destino.get_balance()
    print(f"Saldo de la segunda cuenta: {balance_destino}")
    
    # Verificar si el saldo disponible es suficiente para la operación
    if balance_destino < amount:
        print("Saldo insuficiente en la segunda cuenta.")
        return
    
    # Verificar si la operación ya fue imitada
    if active_id in imitados:
        return
    
    # Ejecutar la orden en la cuenta destino
    print(f"Comprando {amount} dólares en {asset_name}")
    status, order_id = api_destino.buy(int(amount), asset_name, str(direction), expiration)
    
    # Registrar la operación imitada
    imitados.append(active_id)
    
    if status == "open":
        print(f"Orden {order_id} ejecutada")
        result = api_destino.check_win_v3(order_id)
        if result > 0:
            print(f"Orden {order_id} ganadora: {result}")
        elif result < 0:
            print(f"Orden {order_id} perdedora: {result}")

def check_trades():
    global imitados
    positions_origen = api_origen.get_positions()

    if positions_origen[1]['total'] > 0:
        print("Operación encontrada")
        for position in positions_origen[1]['positions']:
            instrument_type = get_instrument_type(position)
            if instrument_type:
                active_id = position['instrument_active_id']
                active_name = position["instrument_underlying"]
                amount = position['buy_amount']
                direction = position['instrument_dir']
                expiration = int(position['instrument_period']) / 60
                imitate_trade(active_id, amount, direction, active_name, expiration)
    else:
        print("Operación no encontrada")

if __name__ == "__main__":
    while True:
        try:
            check_trades()
            time.sleep(10)
        except KeyboardInterrupt:
            print("El bot ha sido detenido.")
            break
