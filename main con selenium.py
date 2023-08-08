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
api_destino = IQ_Option(username_destino, password_destino)

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

# Entrar a la traderoom
driver.get('https://iqoption.com/traderoom')

print("control 6")
# Función para obtener y copiar las operaciones de la primera cuenta

def imitate_trade(active_id, amount, direction, asset_name, expiration):
    # Verificar si la segunda cuenta está conectada
    if not api_destino.check_connect():
        # Si no está conectada, intentar conectar nuevamente
        api_destino.connect()
        if not api_destino.check_connect():
            print("No se pudo conectar a la segunda cuenta.")
            return
    
    # # Obtener el saldo actual de la segunda cuenta utilizando la API
    # balance_destino = api_destino.get_balance()
    # print(f"Saldo de la segunda cuenta: {balance_destino}")
    
    # # Verificar si el saldo disponible es suficiente para la operación
    # if balance_destino < amount:
    #     print("Saldo insuficiente en la segunda cuenta.")
    #     return
    ####################
    # # Encontrar y llenar el formulario de compra en la página web
    # amount_input = driver.find_element(By.XPATH, '//*[@name="sum"]')
    # amount_input.clear()
    # amount_input.send_keys(str(amount))

    # # Encontrar el activo adecuado en la lista (puede variar según el ID del activo)
    # active_item = driver.find_element(By.XPATH, f'//*[@data-id="{active_id}"]')
    # active_item.click()

    # # Encontrar y seleccionar la dirección de la operación
    # if direction == 'call':
    #     call_button = driver.find_element(By.XPATH, '//*[@data-value="call"]')
    #     call_button.click()
    # elif direction == 'put':
    #     put_button = driver.find_element(By.XPATH, '//*[@data-value="put"]')
    #     put_button.click()

    # # Encontrar y hacer clic en el botón de compra
    # buy_button = driver.find_element(By.XPATH, '//*[@data-test="order-button-place-order"]')
    # buy_button.click()
    ######################
    # Esperar a que aparezca el menú desplegable de todos los activos
    all_assets_menu = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'asset')]")))
    all_assets_menu.click()

    # Esperar a que aparezca la barra de búsqueda
    search_bar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'search')]//input")))

    # Escribir el nombre del activo en la barra de búsqueda
    search_bar.send_keys(asset_name)

    # Esperar a que aparezca el activo deseado en los resultados de búsqueda
    asset_result = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'search')]//span[text()='{asset_name}']")))
    
    # Hacer clic en el activo deseado
    asset_result.click()


    ########################

    print(active_id)
    print(amount)
    print(direction)

    # if signal == "buy": # comprar al alza (call)
    print(f"Comprando {amount} dólares en {asset_name}")
    status, order_id = api_destino.buy(amount, asset_name, str(direction), expiration) # ejecutar la orden usando la API
    if status: # la orden se ejecutó correctamente
        print(f"Orden {order_id} ejecutada")
        result = api_destino.check_win_v3(order_id) # verificar el resultado de la orden
        if result > 0: # la orden fue ganadora
            print(f"Orden {order_id} ganadora: {result}")
            amount = 1 # reiniciar el monto de la inversión al valor inicial
        elif result < 0: # la orden fue perdedora
            print(f"Orden {order_id} perdedora: {result}")
            amount = amount * 2 # aplicar el método Martingala y duplicar el monto de la inversión para la próxima orden
    
    # Si hay suficiente saldo, realizar la operación en la segunda cuenta
    # Puedes utilizar Selenium para buscar los elementos en la página y realizar la operación
    # Por ejemplo, puedes utilizar los selectores CSS para seleccionar el activo, ingresar el monto y elegir la dirección
    
    # Después de realizar la operación, esperar un tiempo suficiente para asegurarse de que la operación se haya completado
    # También puedes verificar el estado de la operación para asegurarte de que se haya realizado correctamente
    
    # Puedes agregar más lógica según tus necesidades específicas, como registrar las operaciones realizadas o manejar errores
    pass


def copy_trades():
    # Obtener posiciones abiertas de la primera cuenta
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
            # Llamar a la función para imitar la operación en la segunda cuenta
            imitate_trade(active_id, amount, direction, active_name, expiration)

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