from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
from selenium.webdriver.support.select import Select
from math import floor, ceil

#apretar el boton para buscar
def _search(browser):
    search_button = browser.find_element_by_xpath("//button[@data-qa='search-button']")
    browser.execute_script('arguments[0].click();',search_button)

#las configuraciones que retornan el browser
def _config():
    driver_path = r'/usr/local/bin/chromedriver'
    browser_path = r'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)
    option.binary_location = browser_path
    ## LUEGO DE COMPROBAR QUE FUNCIONE HABILITAR
    #option.add_argument('--headless')
    #option.add_argument("--incognito");
    browser = webdriver.Chrome(executable_path = driver_path, options = option)
    browser.get('https://www.trivago.cl')
    return browser

#boton para apretar siguiente mes en el calendario
def _next_month(browser,wait):
    next_button = wait.until(
        EC.presence_of_element_located(
            (By.CLASS_NAME,'cal-btn-next')
        )
    )
    browser.execute_script('arguments[0].click();', next_button)

#configuracion para habitación familiar y 
def _multiple_room(browser,roomtype,children,child_age,adults,rooms):
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

def _convert_month(checkin):
    year = checkin[0:4]
    monthdict = {
        "Enero" : '01',
        "Febrero" : '02',
        "Marzo" : '03',
        "Abril" : '04',
        "Mayo" : '05',
        "Junio" : '06',
        "Julio" : '07',
        "Agosto" : '08',
        "Septiembre" : '09',
        "Octubre" : '10',
        "Noviembre" : '11',
        "Diciembre" : '12'
    }
    month = list(monthdict.keys())[list(monthdict.values()).index(checkin[5:7])] + " " + year
    return month
    

##### Método
def search_trivago(city, checkin, checkout,rooms, adults, children, babies):
    
    browser = _config()
    #imagino que estos deberíamos estandarizarlo con el main de airbnb
    place = city
    checkin_date = checkin
    checkout_date = checkout

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

    #Transformar fecha a formato de calendario
    month = _convert_month(checkin)
    while arrival_month.text != month:
        #boton que cambia de mes en el calendario
        _next_month(browser,wait)
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
        roomtype_selection = ''
        if rooms == 1 and adults == 1:
            roomtype_selection = 'Individual'
        if rooms == 1 and adults == 2:
            roomtype_selection = 'Doble'
        # CASO EN QUE SE AGREGAN MÁS HABITACIONES
        if rooms > 1:
            roomtype_selection = 'Familiar'
        
        if roomtype_selection == 'Familiar':
            childrens = [] #numero de niños en cada pieza
            child_age = [] #Las edades de los niños de las piezas
            adult = []
            for i in range(int(rooms)):
                adult.append(ceil(adults/rooms))
                print(adults/rooms)
                childrens.append(floor((babies+children)/rooms))
                if int(childrens[i]) > 0:
                    #childroom_age = []
                    for j in range(int(childrens[i])):
                        #Edades niños en una pieza
                        child_age.append('5')
                    #child_age.append(childroom_age)
        #si pide tipo de habitación
            print (adult)
        roomtype_buttons = browser.find_elements_by_class_name('roomtype-btn')
        for roomtype in roomtype_buttons:
            if roomtype.text == roomtype_selection:
                if roomtype.text == 'Individual':
                    browser.execute_script('arguments[0].click();',roomtype)
                    sleep(2)
                    break
                elif roomtype.text == 'Doble':
                    #Se viene en esta opción por defecto
                    break
                elif roomtype.text == 'Familiar':
                    #introducir caso
                    _multiple_room(browser,roomtype,childrens,child_age,adult,rooms)
                    sleep(2)

                    break

        _search(browser)

    except TimeoutException as ex:
        #si la interfaz pide numero de huespedes
        adults_input = wait.until(
            EC.presence_of_element_located(
                (By.ID, 'adults-input')
            )
        )
        adults_input.send_keys(Keys.BACKSPACE)
        adults_input.send_keys('4')
        sleep(1)

        #niños
        children_input = browser.find_element_by_id('children-input')
        children_input.send_keys(Keys.BACKSPACE)
        children_input.send_keys('3')
        sleep(1)

        #habitaciones
        rooms_input = browser.find_element_by_id('rooms-input')
        rooms_input.send_keys(Keys.BACKSPACE)
        rooms_input.send_keys('2')
        sleep(1)

        #edad de los niños
        childs = 3
        for i in range(0,childs):
            dropdown = Select(browser.find_element_by_id('child-{}'.format(i)))
            dropdown.select_by_value('4')
        guest_button = browser.find_element_by_class_name('btn--apply-config')
        browser.execute_script('arguments[0].click();', guest_button)
        sleep(2)
        _search(browser)

    resultados=wait.until(
    EC.presence_of_element_located(
        (By.CLASS_NAME, 'hotel-item')
        )
    )

    contador=1
    #print("Primera oferta")
    precio=[]
    services = []
    resultados=browser.find_elements_by_class_name('hotel-item')
    for resultado in resultados:
        #print(resultado.get_attribute("id"))
        #print(resultado.get_attribute("class"))
        if resultado.get_attribute("class")!='carousel-list__item js_co_item hotel-item':
            #pprint(resultado)
            print("Oferta numero ", contador)
            contador+=1
            nombre = resultado.find_element_by_class_name('name__copytext')
            print("Nombre de la oferta: " + nombre.text)

            precio = resultado.find_element_by_css_selector("strong[class*='accommodation-list__price--']")
            print("Precio por noche: " + precio.text)

            precio_total =resultado.find_element_by_css_selector("span[class*='accommodation-list__pricePerStay--']")
            print("Precio por noche: " + precio_total.text)

            #id_oferta = resultado.get_attribute("id")
            #print(id_oferta)
            #try:
            #    precio_total = resultado.find_element_by_xpath('//*[@id="{}"]/div/article/div[1]/div[2]/section/div[2]/article/div/div[2]/div/em/span'.format(id_oferta))
            #except:
            #    precio_total = resultado.find_element_by_xpath('//*[@id="{}"]/div/article/div[1]/div[2]/section/div[2]/article/div/p/em/span'.format(id_oferta))
            #print("Precio total: " + precio_total.text)

            categoria= resultado.find_element_by_class_name('accommodation-type')
            print("Categoria: " + categoria.text)
            
            id_oferta = resultado.get_attribute("id")
            calificacion = resultado.find_element_by_xpath('//*[@id="{}"]/div/article/div[1]/div[2]/div/div/button/span[1]/span[1]/span'.format(id_oferta))
            print(f'Rating: {calificacion.text} ')
            sleep(3)
        print("\n")

