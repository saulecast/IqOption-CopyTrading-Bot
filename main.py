# input("Pre Control 1")
import sys
# input("Pre Control 2")
import tkinter as tk
from tkinter import ttk
# input("Pre Control 3")
from datetime import datetime
from time import sleep
# input("Pre Control 4")
from threading import Thread
# input("Pre Control 5")
from tkinter import messagebox
# input("Pre Control 6")
try:
    # import iqoptionapi.stable_api
    input("Pre Control 7 ")

    # from iqoptionapi1.iqoptionapi2.stable_api import IQ_Option
    import iqoptionapi.stable_api
except Exception as ex:
    print(ex)
finally:
    input("Control 1 ")


try:
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

            # Fecha límite para el usuario permitido
            expiration_date = datetime(2023, 12, 31)  # Año, mes, día

            # Verificar si el usuario es el permitido
            if username == "uncastilloteorico@gmail.com": #jeestrella15@gmail.com
                # Verificar si la fecha no ha expirado
                if datetime.now() <= expiration_date:
                    print("Usuario permitido y fecha válida")
                    # Puedes continuar con la lógica para copiar operaciones
                else:
                    # Crear ventana principal
                    root = tk.Tk()
                    root.withdraw()  # Ocultar ventana principal
                    messagebox.showerror("Acceso denegado", "Fecha de uso expirada")
                    sys.exit(1)  # Salir del programa con un código de error
            else:
                # Crear ventana principal
                root = tk.Tk()
                root.withdraw()  # Ocultar ventana principal
                messagebox.showerror("Acceso denegado", "Usuario no permitido")
                sys.exit(1)  # Salir del programa con un código de error
            
        return username, password_parts

    # input("Control 2 ")
    # Obtener las credenciales de la segunda cuenta desde el archivo
    username_destino, password_destino = read_second_account_credentials("cuenta.txt")

    # Inicializar la API para ambas cuentas
    api_origen = iqoptionapi.stable_api.IQ_Option(username_origen, password_origen)
    api_destino = iqoptionapi.stable_api.IQ_Option(username_destino, password_destino)
    # input("Control 3 ")

    # Conectar a las cuentas
    api_origen.connect()
    api_destino.connect()

    # Lista para rastrear operaciones ya imitadas
    imitados = []

    # input("Control 4 ")
    def imitate_trade(output_text, instrument_id, original_amount, amount, direction, asset_name, expiration, active_type):
        global imitados

        # Verificar si la operación ya fue imitada
        if instrument_id in imitados:
            print("operación duplicada")
            return
        
        output_text.config(state=tk.NORMAL)
        if direction == "call":
            output_text.insert(tk.END, f"🙈 Operación encontrada: ⬆ por {original_amount} dólares en {asset_name}\n")
        elif direction == "put":
            output_text.insert(tk.END, f"🙈 Operación encontrada: ⬇ por {original_amount} dólares en {asset_name}\n")
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

    def check_trades(output_text, fixed_amount):
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

                        imitate_trade(output_text, instrument_id, amount, fixed_amount, direction, active_name, expiration, "binary-option")
            

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

                    imitate_trade(output_text, instrument_id, amount, fixed_amount, direction, active_name, expiration, "digital-option")


    # import tkinter as tk
    # from tkinter import ttk

    class AmountSelection(tk.Toplevel):
        def __init__(self, parent):
            super().__init__(parent)
            self.title("Selección de Monto")
            
            self.amount_var = tk.DoubleVar()
            self.amount_var.set(10.0)  # Valor predeterminado
            
            label = tk.Label(self, text="Seleccione el monto a gastar en cada operación:")
            label.pack(padx=10, pady=10)
            
            amount_entry = ttk.Entry(self, textvariable=self.amount_var)
            amount_entry.pack(padx=10, pady=10)
            
            confirm_button = ttk.Button(self, text="Confirmar", command=self.confirm_amount)
            confirm_button.pack(pady=10)
        
        def confirm_amount(self):
            selected_amount = self.amount_var.get()
            self.master.set_amount(selected_amount)
            self.destroy()

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
            
            start_button = tk.Button(self, text="Iniciar Bot", command=self.show_amount_selection, bg="#4caf50", fg="white", padx=10, pady=5)
            start_button.pack(pady=10)

            stop_button = tk.Button(self, text="Detener Bot", command=self.stop_bot, bg="#f44336", fg="white", padx=10, pady=5)
            stop_button.pack(pady=5)
            
            # Widget de salida
            self.output_text = tk.Text(self, wrap=tk.WORD, state=tk.DISABLED, bg="white", padx=10, pady=10)
            self.output_text.pack(fill=tk.BOTH, expand=True)
            
        def set_amount(self, amount):
            self.amount = amount
            
        def show_amount_selection(self):
            amount_selection = AmountSelection(self)
            amount_selection.wait_window()
            
            if self.amount is not None:
                self.start_bot()
            
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

    # if __name__ == "__main__":
    # input("Control 5 ")
    app = IQOptionBotApp()
    app.mainloop()
    # input("Control 6 ")

except Exception as ex:
    # from tkinter import messagebox
    # import tkinter as tk
    # import sys

    print(ex)
    # Crear ventana principal
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    messagebox.showerror("Acceso denegado", f"Error, la aplicación no pudo ser iniciada. Por favor informe al desarrollador, error:\n\n{ex}")
    # sys.exit(1)  # Salir del programa con un código de error

# Agrega una pausa para que la consola no se cierre de inmediato
input("Presiona Enter para salir...")