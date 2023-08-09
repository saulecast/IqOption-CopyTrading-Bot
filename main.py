from iqoptionapi.stable_api import IQ_Option
import time
import tkinter as tk
from threading import Thread

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
        print(username)
        print(password)
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

def imitate_trade(instrument_id, amount, direction, asset_name, expiration, active_type):
    global imitados

    # Verificar si la operación ya fue imitada
    if instrument_id in imitados:
        print("operación duplicada")
        return
    
    output_text.config(state=tk.NORMAL)
    if direction == "call":
        output_text.insert(tk.END, f"🙈 Operación encontrada: ⬆ por {amount} dólares en {asset_name}\n")
    elif direction == "put":
        output_text.insert(tk.END, f"🙈 Operación encontrada: ⬇ por {amount} dólares en {asset_name}\n")
    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)
    
    # Obtener el saldo actual de la segunda cuenta utilizando la API
    balance_destino = api_destino.get_balance()
    
    # Verificar si el saldo disponible es suficiente para la operación
    if balance_destino < amount:
        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, f"🙁 Saldo insuficiente: {balance_destino}\n")
        output_text.see(tk.END)
        output_text.config(state=tk.DISABLED)
        return
    
    # Ejecutar la orden en la cuenta destino
    # print(f"Comprando {amount} dólares en {asset_name}")
    if active_type == "binary-option":
        # print("binaria")
        status, order_id = api_destino.buy(price = int(amount), ACTIVES = asset_name, ACTION = "call", expirations = expiration)
    if active_type == "digital-option":
        # print("digital")
        status, order_id = api_destino.buy_digital_spot_v2(active = asset_name, amount = amount, action = direction, duration = expiration)
    
    # print(status)
    # print(order_id)
    
    # Registrar la operación imitada
    imitados.append(instrument_id)
    imitados.append(order_id)
    
    if status == True:
        output_text.config(state=tk.NORMAL)
        if direction == "call":
            output_text.insert(tk.END, f"🙉Operación copiada: ⬆ por {amount} dólares en {asset_name}\n----------------------------------\n")
        elif direction == "put":
            output_text.insert(tk.END, f"🙉Operación copiada: ⬇ por {amount} dólares en {asset_name}\n----------------------------------\n")
        output_text.see(tk.END)
        output_text.config(state=tk.DISABLED)

        # result = api_destino.check_win_v3(order_id)
        # if result > 0:
        #     print(f"Orden {order_id} ganadora: {result}")
        # elif result < 0:
        #     print(f"Orden {order_id} perdedora: {result}")

def check_trades():
    global imitados
    positions_origen = api_origen.get_positions("digital-option")

    ### No se encontraron posiciones digitales, intenando con las binarias
    if positions_origen[1]['total'] == 0:
        # Obtiene las posiciones de opciones binarias abiertas desde otro dispositivo o desde la web
        positions_origen = api_origen.get_option_open_by_other_pc()
        # print(len(positions_origen))
        
        ## Se encontraron posiciones activas con opciones binarias
        if len(positions_origen) != 0:
            # print(positions_origen)

            for id, position in positions_origen.copy().items(): # usamos una copia porque este diccionario de posiciones cambiará cuando se copie una operación
                instrument_id = id
                # Verificar si la operación ya fue imitada
                if instrument_id in imitados:
                    # print("operación duplicada")
                    pass
                else:
                    output_text.config(state=tk.NORMAL)
                    output_text.insert(tk.END, f"2️⃣ Operación binaria encontrada\n")
                    output_text.see(tk.END)
                    output_text.config(state=tk.DISABLED)

                    # Supongamos que el diccionario se llama positions
                    active_name = position["msg"]["active"]
                    amount = int(int(position["msg"]["amount"])/1000000)
                    direction = position["msg"]["dir"]
                    # expiration = int(position["msg"]["exp_time"] - position["msg"]["created"])
                    expiration = 1
                    # # Obtiene el id de la posición
                    # print("Id:", id)
                    # # Obtiene el nombre de la posición
                    # print("Nombre:", active_name)
                    # # Obtiene la cantidad invertida
                    # print("Cantidad:", amount)
                    # # Obtiene la dirección (call o put)
                    # print("Dirección:", direction)
                    # # Obtiene el periodo de expiración en segundos
                    # print("Periodo:", expiration)

                    imitate_trade(instrument_id, amount, direction, active_name, expiration, "binary-option")
        

    ### Se encontraron posiciones activas con opciones digitales
    elif positions_origen[1]['total'] > 0:
        # print(positions_origen)

        for position in positions_origen[1]['positions']:
            instrument_id = position['instrument_id']
            # Verificar si la operación ya fue imitada
            if instrument_id in imitados:
                # print("operación duplicada")
                pass
            else:
                output_text.config(state=tk.NORMAL)
                output_text.insert(tk.END, f"🅾️ Operación digital encontrada\n")
                output_text.see(tk.END)
                output_text.config(state=tk.DISABLED)

                # instrument_active_id = position['instrument_active_id']
                # active_id = position['id']
                active_name = position["instrument_underlying"]
                amount = position['buy_amount']
                direction = position['instrument_dir']
                expiration = int(int(position['instrument_period']) / 60)

                # # Obtiene el id de la posición
                # print("Id:", active_id)
                # # Obtiene el nombre de la posición
                # print("Nombre:", active_name)
                # # Obtiene la cantidad invertida
                # print("Cantidad:", amount)
                # # Obtiene la dirección (call o put)
                # print("Dirección:", direction)
                # # Obtiene el periodo de expiración en segundos
                # print("Periodo:", expiration)

                imitate_trade(instrument_id, amount, direction, active_name, expiration, "digital-option")

if __name__ == "__main__":
    # Declaración de la variable del hilo del bot para poder globalizar
    bot_thread = None
    # Variable de control para activar/detener el bucle
    running = False

    def start_bot():
        global bot_thread
        global running

        def run():
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, "Bot en ejecución...\n")
            output_text.see(tk.END)
            output_text.config(state=tk.DISABLED)

            while running:
                try:
                    check_trades()
                    time.sleep(10)
                except KeyboardInterrupt:
                    # print("El bot ha sido detenido.")
                    break

        if not running:
            running = True
            bot_thread = Thread(target=run)
            bot_thread.start()

    def stop_bot():
        global bot_thread
        global running

        def stop():
            if bot_thread:
                bot_thread.join()

        if running:
            running = False
            stop_thread = Thread(target=stop)
            stop_thread.start()
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, "Bot detenido.\n")
            output_text.see(tk.END)
            output_text.config(state=tk.DISABLED)

    root = tk.Tk()
    root.title("IQ Option Bot")

    # Mejora de la apariencia
    root.geometry("300x400")
    root.configure(bg="#f0f0f0")

    start_button = tk.Button(root, text="Iniciar Bot", command=start_bot, bg="#4caf50", fg="white", padx=10, pady=5)
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Detener Bot", command=stop_bot, bg="#f44336", fg="white", padx=10, pady=5)
    stop_button.pack(pady=5)

    # Widget de salida
    output_text = tk.Text(root, wrap=tk.WORD, state=tk.DISABLED, bg="white", padx=10, pady=10)
    output_text.pack(fill=tk.BOTH, expand=True)

    root.mainloop()