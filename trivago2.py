from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
from selenium.webdriver.support.select import Select

#apreta el boton para buscar
def search(browser):
    search_button = browser.find_element_by_xpath("//button[@data-qa='search-button']")
    browser.execute_script('arguments[0].click();',search_button)

#las configuraciones que retornan el browser
def config():
    driver_path = r'/usr/local/bin/chromedriver'
    browser_path = r'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
    option = webdriver.ChromeOptions()
    option.binary_location = browser_path
    ## LUEGO DE COMPROBAR QUE FUNCIONE HABILITAR
    #option.add_argument('--headless')
    browser = webdriver.Chrome(executable_path = driver_path, options = option)
    return browser

#boton para apretar siguiente mes en el calendario
def next_month(browser,wait):
    next_button = wait.until(
        EC.presence_of_element_located(
            (By.CLASS_NAME,'cal-btn-next')
        )
    )
    browser.execute_script('arguments[0].click();', next_button)

#configuracion para habitación familiar y 
def multiple_room(browser,roomtype,children,child_age,adults,rooms):
    browser.execute_script('arguments[0].click();',roomtype)
    for i in range(int(rooms)-1):
        add_room = browser.find_element_by_class_name('add_room')
        browser.execute_script('arguments[0].click();',add_room) 
    sleep(0.5)

    for i in range(int(rooms)):
        adults_input = browser.find_element_by_id('select-num-adults-{}'.format(i+2))
        adults_input.send_keys(adults[i])
        children_input = browser.find_element_by_id('select-num-children-{}'.format(i+2))
        children_input.send_keys(children[i])
        sleep(0.5)
        children_ages = browser.find_elements_by_class_name('js-select-child-age')
        
        #SE AGREGAN LAS EDADES DE LOS MENORES DE EDAD
        j = 0
        for room_age in children_ages:
            room_age.send_keys(child_age[j])
            j += 1

    ok_button = browser.find_element_by_class_name('confirm')
    browser.execute_script('arguments[0].click();', ok_button)

        
browser = config()
browser.get('https://www.trivago.cl')
place = input('Escriba el nombre de la ciudad de destino: ')
checkin_date = input('Escriba la fecha de llegada (YYYY-MM-DD): ')
checkout_date = input('Escriba la fecha de salida (YYY-MM-DD):')

#escribir la ciudad de destino
wait = WebDriverWait(browser, 5)
place_input = wait.until(
    EC.presence_of_element_located(
        (By.ID, 'querytext')
    )
)
place_input.send_keys(place)

## boton que abre el calendario
checkin_button = browser.find_element_by_xpath("//button[@key = 'checkInButton']")
browser.execute_script('arguments[0].click();', checkin_button)

#encontrar el mes en el que se llegará
arrival_month = wait.until(
    EC.presence_of_element_located(
        (By.XPATH,"//*[@id='cal-heading-month']/span")
    )
)

while arrival_month.text != 'Octubre 2020':
    #boton que cambia de mes en el calendario
    next_month(browser,wait)
    arrival_month = wait.until(
        EC.presence_of_element_located(
            (By.XPATH,"//*[@id='cal-heading-month']/span")
        )
    )

arrival_dates = browser.find_elements_by_xpath("//*[@id='js-fullscreen-hero']/div[1]/form/div[4]/div[2]/div/table /tbody/tr/td/time")
for date in arrival_dates:
    if date.get_attribute('datetime') == checkin_date:
        browser.execute_script('arguments[0].click();',date)
        break
sleep(1)

departure_dates = browser.find_elements_by_xpath("//*[@id='js-fullscreen-hero']/div[1]/form/div[4]/div[2]/div/table /tbody/tr/td/time")

for date in departure_dates:
    if date.get_attribute('datetime') == checkout_date:
        browser.execute_script('arguments[0].click();',date)
        break


#Casos dependiendo del boton para elegir habitaciones o huespedes
try:
    roomtype_selection = input("Que tipo de habitación desea: ")
    # CASO EN QUE SE AGREGAN MÁS HABITACIONES
    if roomtype_selection == 'Familiar' or roomtype_selection ==  'Múltiple':
        rooms = input('Ingrese el numero de habitaciones: ')
        children = [] #numero de niños en cada pieza
        child_age = [] #Las edades de los niños de las piezas
        adults = []
        for i in range(int(rooms)):
            adults.append(input('Ingrese el numero de mayores de edad en la habitación: '))
            children.append(input("Ingrese el numero de menores de edad en la habitación: "))
            if int(children[i]) > 0:
                #childroom_age = []
                for j in range(int(children[i])):
                    #Edades niños en una pieza
                    child_age.append(input(f'Ingrese edad del menor {j+1}: '))
                #child_age.append(childroom_age)
    #si pide tipo de habitación
    roomtype_buttons = browser.find_elements_by_class_name('roomtype-btn')
    for roomtype in roomtype_buttons:
        if roomtype.text == roomtype_selection:
            if roomtype.text == 'Individual':
                browser.execute_script('arguments[0].click();',roomtype)
                break
            elif roomtype.text == 'Doble':
                #Se viene en esta opción por defecto
                break
            elif roomtype.text == 'Familiar':
                #introducir caso
                multiple_room(browser,roomtype,children,child_age,adults,rooms)
                    
                break
            elif roomtype.text == 'Múltiple':
                multiple_room(browser,roomtype,children,child_age,adults,rooms)
                break
    
    search(browser)

except TimeoutException as ex:
    #si la interfaz pide numero de huespedes
    adults_input = wait.until(
        EC.presence_of_element_located(
            (By.ID, 'adults-input')
        )
    )
    adults_input.send_keys(Keys.BACKSPACE)
    adults_input.send_keys('4')
    sleep(0.5)

    #niños
    children_input = browser.find_element_by_id('children-input')
    children_input.send_keys(Keys.BACKSPACE)
    children_input.send_keys('3')
    sleep(0.5)

    #habitaciones
    rooms_input = browser.find_element_by_id('rooms-input')
    rooms_input.send_keys(Keys.BACKSPACE)
    rooms_input.send_keys('2')
    sleep(0.5)

    #edad de los niños
    childs = 3
    for i in range(0,childs):
        dropdown = Select(browser.find_element_by_id('child-{}'.format(i)))
        dropdown.select_by_value('4')
    guest_button = browser.find_element_by_class_name('btn--apply-config')
    browser.execute_script('arguments[0].click();', guest_button)
    sleep(0.5)
    search(browser)