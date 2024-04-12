import sys
from datetime import datetime
from time import sleep
from threading import Thread
from iqoptionapi.stable_api import IQ_Option



# Credenciales para las cuentas
username_origen = 'ejemplo@gmail.com'
password_origen = 'contraseña'

class Trade():
    def __init__(self, username_destino, password_destino, bot, chat_id):
        
        #connection to telegram bot
        self.bot = bot
        self.chat_id = chat_id

        # Inicializar la API para ambas cuentas
        self.api_origen = IQ_Option(username_origen, password_origen)
        self.api_destino = IQ_Option(username_destino, password_destino)

        # Conectar a las cuentas
        self.api_origen.connect()
        self.api_destino.connect()

        # Lista para rastrear operaciones ya imitadas
        self.imitados = []

    def imitate_trade(self, output_text, instrument_id, original_amount, amount, direction, asset_name, expiration, active_type):

        # Verificar si la operación ya fue imitada
        if instrument_id in self.imitados:
            print("operación duplicada")
            return
            
        if direction == "call":
            self.bot.send_message(
                self.chat_id,
                f"🙈 Operación encontrada: ⬆ por {original_amount} dólares en {asset_name}\n")
        elif direction == "put":
            self.bot.send_message(
                self.chat_id,
                f"🙈 Operación encontrada: ⬇ por {original_amount} dólares en {asset_name}\n")
        
        # Obtener el saldo actual de la segunda cuenta utilizando la API
        balance_destino = self.api_destino.get_balance()
        
        # Verificar si el saldo disponible es suficiente para la operación
        if balance_destino < amount:
            self.bot.send_message(
                self.chat_id,
                f"🙁 Saldo insuficiente: {balance_destino}\n")
            return
        
        # Ejecutar la orden en la cuenta destino
        # print(f"Comprando {amount} dólares en {asset_name}")
        if active_type == "binary-option":
            # print("binaria")
            status, order_id = self.api_destino.buy(price = int(amount), ACTIVES = asset_name, ACTION = "call", expirations = expiration)
        if active_type == "digital-option":
            # print("digital")
            status, order_id = self.api_destino.buy_digital_spot_v2(active = asset_name, amount = amount, action = direction, duration = expiration)
        
        # print(status)
        # print(order_id)
        
        # Registrar la operación imitada
        self.imitados.append(instrument_id)
        self.imitados.append(order_id)
        
        if status == True:
            if direction == "call":
                self.bot.send_message(
                    self.chat_id,
                    f"🙉Operación copiada: ⬆ por {amount} dólares en {asset_name}")
            elif direction == "put":
                self.bot.send_message(
                    self.chat_id,
                    f"🙉Operación copiada: ⬇ por {amount} dólares en {asset_name}")

            # result = self.api_destino.check_win_v3(order_id)
            # if result > 0:
            #     print(f"Orden {order_id} ganadora: {result}")
            # elif result < 0:
            #     print(f"Orden {order_id} perdedora: {result}")

    def check_trades(self, output_text, fixed_amount):

        positions_origen = self.api_origen.get_positions("digital-option")

        ### No se encontraron posiciones digitales, intenando con las binarias
        if positions_origen[1]['total'] == 0:
            # Obtiene las posiciones de opciones binarias abiertas desde otro dispositivo o desde la web
            positions_origen = self.api_origen.get_option_open_by_other_pc()
            # print(len(positions_origen))
            
            ## Se encontraron posiciones activas con opciones binarias
            if len(positions_origen) != 0:
                # print(positions_origen)

                for id, position in positions_origen.copy().items(): # usamos una copia porque este diccionario de posiciones cambiará cuando se copie una operación
                    instrument_id = id
                    # Verificar si la operación ya fue imitada
                    if instrument_id in self.imitados:
                        # print("operación duplicada")
                        pass
                    else:
                        self.bot.send_message(
                            self.chat_id,
                            f"2️⃣ Operación binaria encontrada")

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

                        self.imitate_trade(output_text, instrument_id, amount, fixed_amount, direction, active_name, expiration, "binary-option")
            

        ### Se encontraron posiciones activas con opciones digitales
        elif positions_origen[1]['total'] > 0:
            # print(positions_origen)

            for position in positions_origen[1]['positions']:
                instrument_id = position['instrument_id']
                # Verificar si la operación ya fue imitada
                if instrument_id in self.imitados:
                    # print("operación duplicada")
                    pass
                else:
                    self.bot.send_message(
                            self.chat_id,
                            f"🅾️ Operación digital encontrada")

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

                    self.imitate_trade(output_text, instrument_id, amount, fixed_amount, direction, active_name, expiration, "digital-option")


class IQOptionBotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IQ Option Bot")
        
        self.amount = None  # Variable para almacenar el monto seleccionado

        # Declaración de la variable del hilo del bot para poder globalizar
        self.bot_thread = None
        # Variable de control para activar/detener el bucle
        self.running = False
        
        # Mejora de la apariencia
        self.geometry("300x400")
        self.configure(bg="#f0f0f0")
        
        start_button = tk.Button(self, text="Iniciar Bot", command=self.start_bot, bg="#4caf50", fg="white", padx=10, pady=5)
        start_button.pack(pady=10)

        stop_button = tk.Button(self, text="Detener Bot", command=self.stop_bot, bg="#f44336", fg="white", padx=10, pady=5)
        stop_button.pack(pady=5)
        
        # Widget de salida
        self.output_text = tk.Text(self, wrap=tk.WORD, state=tk.DISABLED, bg="white", padx=10, pady=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
        
    def start_bot(self):
        def run():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, "Bot en ejecución...\n")
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)

            while self.running:
                try:
                    check_trades(self.output_text, self.amount)
                    sleep(10)
                except KeyboardInterrupt:
                    print("El bot ha sido detenido.")
                    break

        if not self.running:
            self.running = True
            self.bot_thread = Thread(target=run)
            self.bot_thread.start()
        
    def stop_bot(self):

        def stop():
            if self.bot_thread:
                self.bot_thread.join()

        if self.running:
            self.running = False
            stop_thread = Thread(target=stop)
            stop_thread.start()
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, "Bot detenido.\n")
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)

