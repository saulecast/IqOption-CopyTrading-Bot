import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, filters
import sys
from datetime import datetime
from time import sleep
from threading import Thread
from telegram import Bot
from queue import Queue

from iqoptionapi.stable_api import IQ_Option

# Configura el registro
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Credenciales para las cuentas
username_origen = 'ejemplo@gmail.com'
password_origen = 'contraseña'

# Leer las credenciales de la segunda cuenta desde el archivo
def read_second_account_credentials(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        username = lines[0].strip().split(":")[1].strip()
        password_parts = lines[1].strip().split(": ")[1:]
        password = "".join(password_parts)
        print(username)
        print(password)

        # Fecha límite para el usuario permitido
        expiration_date = datetime(2023, 12, 31)  # Año, mes, día

        # Verificar si el usuario es el permitido
        if username == "ejemplo@gmail.com": #jeestrella15@gmail.com
            # Verificar si la fecha no ha expirado
            if datetime.now() <= expiration_date:
                print("Usuario permitido y fecha válida")
                # Puedes continuar con la lógica para copiar operaciones
            else:
                raise Exception("Fecha de uso expirada")
        else:
            raise Exception("Usuario no permitido")
        
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

def imitate_trade(instrument_id, original_amount, amount, direction, asset_name, expiration, active_type):
    global imitados

    # Verificar si la operación ya fue imitada
    if instrument_id in imitados:
        print("operación duplicada")
        return
    
    if direction == "call":
        message = f"🙈 Operación encontrada: ⬆ por {original_amount} dólares en {asset_name}"
    elif direction == "put":
        message = f"🙈 Operación encontrada: ⬇ por {original_amount} dólares en {asset_name}"
    print(message)
    
    # Obtener el saldo actual de la segunda cuenta utilizando la API
    balance_destino = api_destino.get_balance()
    
    # Verificar si el saldo disponible es suficiente para la operación
    if balance_destino < amount:
        print(f"🙁 Saldo insuficiente: {balance_destino}")
        return
    
    # Ejecutar la orden en la cuenta destino
    if active_type == "binary-option":
        status, order_id = api_destino.buy(price=int(amount), ACTIVES=asset_name, ACTION="call", expirations=expiration)
    elif active_type == "digital-option":
        status, order_id = api_destino.buy_digital_spot_v2(active=asset_name, amount=amount, action=direction, duration=expiration)
    
    # Registrar la operación imitada
    imitados.append(instrument_id)
    imitados.append(order_id)
    
    if status == True:
        if direction == "call":
            message = f"🙉Operación copiada: ⬆ por {amount} dólares en {asset_name}\n----------------------------------"
        elif direction == "put":
            message = f"🙉Operación copiada: ⬇ por {amount} dólares en {asset_name}\n----------------------------------"
        print(message)

def check_trades(fixed_amount):
    global imitados
    positions_origen = api_origen.get_positions("digital-option")

    if positions_origen[1]['total'] == 0:
        positions_origen = api_origen.get_option_open_by_other_pc()
        
        if len(positions_origen) != 0:
            for id, position in positions_origen.copy().items():
                instrument_id = id
                if instrument_id not in imitados:
                    active_name = position["msg"]["active"]
                    amount = int(int(position["msg"]["amount"]) / 1000000)
                    direction = position["msg"]["dir"]
                    expiration = 1
                    imitate_trade(instrument_id, amount, fixed_amount, direction, active_name, expiration, "binary-option")
    elif positions_origen[1]['total'] > 0:
        for position in positions_origen[1]['positions']:
            instrument_id = position['instrument_id']
            if instrument_id not in imitados:
                active_name = position["instrument_underlying"]
                amount = position['buy_amount']
                direction = position['instrument_dir']
                expiration = int(int(position['instrument_period']) / 60)
                imitate_trade(instrument_id, amount, fixed_amount, direction, active_name, expiration, "digital-option")

# Variables para controlar el estado del bot
bot_running = False
bot_thread = None

# Función para manejar el comando /start
def start(update: Update, context: CallbackContext) -> None:
    global bot_running, bot_thread

    if bot_running:
        update.message.reply_text('El bot ya está en ejecución.')
    else:
        update.message.reply_text('Iniciando el bot...')
        bot_running = True
        bot_thread = Thread(target=run_bot)
        bot_thread.start()

# Función para manejar el comando /stop
def stop(update: Update, context: CallbackContext) -> None:
    global bot_running, bot_thread

    if bot_running:
        update.message.reply_text('Deteniendo el bot...')
        bot_running = False
        if bot_thread:
            bot_thread.join()
            bot_thread = None
        update.message.reply_text('El bot ha sido detenido.')
    else:
        update.message.reply_text('El bot no está en ejecución.')

# Función que ejecuta el bot en segundo plano
def run_bot():
    fixed_amount = 10.0  # Monto fijo para copiar operaciones

    while bot_running:
        try:
            check_trades(fixed_amount)
            sleep(10)
        except KeyboardInterrupt:
            print("El bot ha sido detenido.")
            break

# Función para manejar otros mensajes
def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('No entiendo ese comando. Envíame un comando válido.')


def main() -> None:
    # TOKEN de tu bot de Telegram
    TOKEN = "6699468197:AAEXYyXZfB2fNoNc-NwB45XKADz0LZJTY7s"

    # Crear una instancia de telegram.Bot con el token
    bot = Bot(token=TOKEN)

    # Crear una instancia de Updater utilizando la instancia de Bot
    updater = Updater(bot=bot, update_queue=Queue())

    # Obtener el dispatcher desde la instancia de Updater
    dispatcher = updater.dispatcher_

    # Manejadores de comandos y mensajes
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(MessageHandler(filters.text & ~filters.command, echo))

    # Inicia el bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    # try:
    main()
    # except Exception as ex:
    #     print(ex)
