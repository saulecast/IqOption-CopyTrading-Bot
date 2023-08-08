# Importar las librerías necesarias
import numpy as np
import pandas as pd
import talib as ta
from iqoptionapi.stable_api import IQ_Option
from time import sleep

# Definir las variables globales
email = "uncastilloteorico@gmail.com"
password = "Esesan:29a8D8Xv"
currency = "EURUSD"
expiration = 1 # minuto
amount = 1 # dólar

# Conectar con la API de IQ Option y verificar el saldo
API = IQ_Option(email, password)
API.connect()
balance = API.get_balance()
print(f"Saldo: {balance}")

# Definir una función para obtener los datos históricos de los precios
def get_data():
    candles = API.get_candles(currency, 60, 100, 0) # obtener 100 velas de 1 minuto
    data = pd.DataFrame(candles, columns=["id", "from", "at", "to", "open", "close", "min", "max", "volume"])
    data.drop(["id", "at", "volume"], axis=1, inplace=True) # eliminar columnas innecesarias
    data.set_index("from", inplace=True) # usar la columna from como índice
    return data

# Definir una función para calcular los indicadores técnicos
def get_indicators(data):
    upper, middle, lower = ta.BBANDS(data["close"], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0) # bandas de Bollinger
    rsi = ta.RSI(data["close"], timeperiod=14) # índice de fuerza relativa
    macd, macdsignal, macdhist = ta.MACD(data["close"], fastperiod=12, slowperiod=26, signalperiod=9) # media móvil de convergencia/divergencia
    data["upper"] = upper
    data["middle"] = middle
    data["lower"] = lower
    data["rsi"] = rsi
    data["macd"] = macd
    data["macdsignal"] = macdsignal
    data["macdhist"] = macdhist
    return data

# Definir una función para evaluar las señales de compra o venta
def get_signals(data):
    buy = []
    sell = []
    for i in range(len(data)):
        if data["lower"][i] > data["close"][i] and data["rsi"][i] < 30 and data["macd"][i] > data["macdsignal"][i]: # condición de compra
            buy.append(1)
            sell.append(0)
        elif data["upper"][i] < data["close"][i] and data["rsi"][i] > 70 and data["macd"][i] < data["macdsignal"][i]: # condición de venta
            buy.append(0)
            sell.append(1)
        else: # ninguna condición se cumple
            buy.append(0)
            sell.append(0)
    data["buy"] = buy
    data["sell"] = sell
    return data

# Definir una función para ejecutar las órdenes de compra o venta y verificar el resultado
# def execute_order(signal):
def execute_order():
    global amount # usar la variable global amount
    # if signal == "buy": # comprar al alza (call)
    print(f"Comprando {amount} dólares en {currency}")
    status, order_id = API.buy(amount, currency, "call", expiration) # ejecutar la orden usando la API
    if status: # la orden se ejecutó correctamente
        print(f"Orden {order_id} ejecutada")
        result = API.check_win_v3(order_id) # verificar el resultado de la orden
        if result > 0: # la orden fue ganadora
            print(f"Orden {order_id} ganadora: {result}")
            amount = 1 # reiniciar el monto de la inversión al valor inicial
        elif result < 0: # la orden fue perdedora
            print(f"Orden {order_id} perdedora: {result}")
            amount = amount * 2 # aplicar el método Martingala y duplicar el monto de la inversión para la próxima orden

def copy_trades():
    # Inicializar la API de IQ Option para la primera cuenta (cuenta que copiaremos)
    api_origen = IQ_Option(email, password)

    # Iniciar sesión en la API para la primera cuenta
    api_origen.connect()

    # Esperar hasta que la conexión esté establecida
    api_origen.check_connect()

    # Obtener posiciones abiertas de la primera cuenta
    instrument_type = "digital-option"
    positions_origen = api_origen.get_positions(instrument_type)
    print(positions_origen)

    if positions_origen[1]['total'] > 0:
        print("Operación encontrada")
        # Copiar las operaciones en la segunda cuenta usando Selenium
        for position in positions_origen[1]['positions']:
            active_id = position['instrument_active_id']
            active_name = position["instrument_underlying"]
            amount = position['count']
            direction = position['instrument_dir']
            expiration = position['instrument_expiration']
            # print(expiration)

            # Llamar a la función para imitar la operación en la segunda cuenta
            execute_order()

if __name__ == "__main__":
    # while True:
    #     try:
    #         # # Obtener los datos históricos de los precios
    #         # data = get_data()
    #         # print(data)
    #         # # Calcular los indicadores técnicos y evaluar las señales de compra o venta
    #         # data = get_indicators(data)
    #         # data = get_signals(data)
    #         # # Ejecutar la orden según la señal
    #         # signal = data["buy"].iloc[-1] # comprar al alza si la columna buy es 1

    #         #########


    #         #########


    #         execute_order(signal)
    #         # Esperar 60 segundos hasta la próxima iteración
    #         sleep(30)
    #     except KeyboardInterrupt:
    #         # Manejar la interrupción del teclado (Ctrl + C) para detener el bot
    #         print("El bot ha sido detenido.")
    #         break
    #     except Exception as ex:
    #         # print(ex)
    #         if str(ex) == "inputs are all NaN": #sin operación presente
    #             pass
    #         sleep(30)

    while True:
        try:
            # Copiar las operaciones de la primera cuenta y realizarlas en la segunda cuenta cada 30 segundos
            copy_trades()
            sleep(20)
        except KeyboardInterrupt:
            # Manejar la interrupción del teclado (Ctrl + C) para detener el bot
            print("El bot ha sido detenido.")
            break
