from iqoptionapi.stable_api import IQ_Option
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from fake_useragent import UserAgent
from selenium_stealth import stealth

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Función para configurar las opciones del navegador Chrome con medidas de seguridad
def configure_chrome_options():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument("--disable-notifications")
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # options.add_experimental_option("prefs", prefs)
    # options.add_argument("--disable-infobars")
    # options.add_argument("disable-extensions")

    # user_agent = UserAgent().random
    # options.add_argument(f'user-agent={user_agent}')
    # options.add_argument("--window-size=1920,1080")
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--allow-running-insecure-content')
    # options.add_argument("--disable-extensions")
    # options.add_argument("--proxy-server='direct://'")
    # options.add_argument("--proxy-bypass-list=*")
    # options.add_argument("--start-maximized")
    # options.add_argument('--disable-gpu')
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--no-sandbox')

    return options

# Credenciales y URLs para las cuentas
username_origen = 'uncastilloteorico@gmail.com'
password_origen = 'Esesan:29a8D8Xv'
username_destino = 'uncastilloteorico@gmail.com'
password_destino = 'Esesan:29a8D8Xv'
instrument_type = "digital-option"

print("control 1")
# Inicializar la API de IQ Option para la primera cuenta (cuenta que copiaremos)
api_origen = IQ_Option(username_origen, password_origen)
api_destino = IQ_Option(username_origen, password_origen)

# Iniciar sesión en la API para la primera cuenta
api_origen.connect()

# Esperar hasta que la conexión esté establecida
api_origen.check_connect()

# Configurar opciones para el navegador Chrome con medidas de seguridad
options = configure_chrome_options()

print("control 2")
# Crear una instancia del servicio de Chrome
service = ChromeService(executable_path='C:/path/to/chromedriver.exe')

print("control 3")
# Iniciar el navegador Chrome con medidas de seguridad
driver = webdriver.Chrome(service=service, options=options)

# Ocultar el User-Agent del navegador con medidas de seguridad
stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

print("control 4")
# Iniciar sesión en la segunda cuenta utilizando Selenium
driver.get('https://iqoption.com/login')

# Esperar hasta que la página se cargue completamente y el elemento de inicio de sesión esté presente
wait = WebDriverWait(driver, 30)
email_input = wait.until(EC.presence_of_element_located((By.NAME, 'identifier')))

print("control 5")
# Realizar el inicio de sesión en la segunda cuenta
email_input.send_keys(username_destino)
driver.find_element(By.NAME, 'password').send_keys(password_destino)

# Esperar antes de hacer clic en el botón para asegurarte de que la página esté completamente cargada
time.sleep(5)

# Hacer clic en el botón "Iniciar Sesión" utilizando JavaScript
submit_button = driver.find_element(By.CSS_SELECTOR, '[data-test-id="login-submit-button"]')

driver.execute_script("arguments[0].click();", submit_button)
time.sleep(10)

print("control 6")
# Función para obtener y copiar las operaciones de la primera cuenta


def copy_trades():
    # Obtener posiciones abiertas de la primera cuenta
    positions_origen = api_origen.get_positions(instrument_type)
    print(positions_origen)

    if positions_origen[1]['total'] > 0:
        print("Operación encontrada")
        # Copiar las operaciones en la segunda cuenta usando Selenium
        for position in positions_origen[1]['positions']:
            active_id = position['instrument_active_id']
            amount = position['count']
            direction = position['instrument_dir']
            # Verificar si el saldo es suficiente para realizar la operación en la primera cuenta
            balance_origen = api_origen.get_balance()
            if balance_origen >= amount:
                # Realizar la operación en la primera cuenta utilizando la API de IQ Option
                result = api_origen.buy(amount, active_id, direction, instrument_type)
                if result:
                    print("Operación realizada en la primera cuenta.")
                    # Puedes agregar más lógica aquí, como registrar la operación o realizar otras acciones
                else:
                    print("No se pudo realizar la operación en la primera cuenta.")
            else:
                print("Saldo insuficiente en la primera cuenta para realizar la operación.")

        # Luego de copiar todas las operaciones, esperar antes de copiar nuevamente
        time.sleep(30)

if __name__ == "__main__":
    while True:
        try:
            # Copiar las operaciones de la primera cuenta y realizarlas en la segunda cuenta cada 30 segundos
            copy_trades()
            time.sleep(10)
        except KeyboardInterrupt:
            # Manejar la interrupción del teclado (Ctrl + C) para detener el bot
            print("El bot ha sido detenido.")
            break

# Cerrar el navegador web al finalizar
driver.quit()