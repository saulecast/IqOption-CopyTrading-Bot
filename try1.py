from iqoptionapi.stable_api import IQ_Option
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService


print(chromedriver_autoinstaller.get_chrome_version())

# Credenciales de inicio de sesión para la primera cuenta (cuenta que copiaremos)
username_origen = 'uncastilloteorico@gmail.com'
password_origen = 'Esesan:29a8D8Xv'
instrument_type = "digital-option"

# Credenciales de inicio de sesión para la segunda cuenta (cuenta donde se realizarán las operaciones)
username_destino = 'uncastilloteorico@gmail.com'
password_destino = 'Esesan:29a8D8Xv'

# Inicializar la API de IQ Option para la primera cuenta (cuenta que copiaremos)
api_origen = IQ_Option(username_origen, password_origen)

# Iniciar sesión en la API para la primera cuenta
api_origen.connect()

# Esperar hasta que la conexión esté establecida
api_origen.check_connect()

print("pre-control 1")
# Configurar opciones para el navegador Chrome
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

# Crear una instancia del servicio de Chrome
service = ChromeService(executable_path='C:/path/to/chromedriver.exe')

# Iniciar el navegador Chrome
driver = webdriver.Chrome(service=service, options=options)

# Iniciar sesión en la segunda cuenta utilizando Selenium
driver.get('https://iqoption.com/login')

# Esperar 10 segundos para que la página se cargue completamente
time.sleep(10)

# Buscar el elemento "email" utilizando un selector CSS diferente
driver.find_element(By.CSS_SELECTOR, 'input[name="email"]').send_keys(username_destino)
driver.find_element(By.NAME, 'password').send_keys(password_destino)
driver.find_element(By.ID, 'login-btn').click()
time.sleep(10)
print("control 2")

# Función para obtener y copiar las operaciones de la primera cuenta
def copy_trades():
    # Obtener posiciones abiertas de la primera cuenta
    positions_origen = api_origen.get_positions(instrument_type)
    print(positions_origen)
    
    if positions_origen['total'] > 0:
        print("Operación encontrada")
        # Copiar las operaciones en la segunda cuenta usando Selenium
        for position in positions_origen['positions']:
            direction = position['type']
            amount = position['count']
            # Aquí puedes agregar el código para realizar la operación en la segunda cuenta con Selenium
            # Por ejemplo, puedes utilizar el navegador para comprar el mismo activo en la segunda cuenta.

if __name__ == "__main__":
    print("control 3")
    while True:
        try:
            print("control 4")

            # Copiar las operaciones de la primera cuenta y realizarlas en la segunda cuenta cada 30 segundos
            copy_trades()
            time.sleep(6)
        except KeyboardInterrupt:
            # Manejar la interrupción del teclado (Ctrl + C) para detener el bot
            print("El bot ha sido detenido.")
            break

# Cerrar el navegador web al finalizar
driver.quit()
