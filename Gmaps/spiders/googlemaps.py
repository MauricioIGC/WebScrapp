import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains #para mover el mouse y teclear
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from selenium.webdriver.common.keys import Keys
from Gmaps.items import GmapsItem #importamos el archivo items.py
from scrapy.http import HtmlResponse
import gc
import pandas as pd

'''No dar clicks ni mover el mouse mientras se ejecuta el código'''

class GoogleMapas(scrapy.Spider):
    name = 'googlemaps'
    start_urls = ['https://www.google.com/maps/']

    # Usando un dummy ficticio para scrapy request
    def start_requests(self):
        url = "https://www.google.com/maps"
        yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        #Iniciamos el webdriver
        options = webdriver.firefox.options.Options()
        options.headless = False  #True para no abrir el navegador   
        ''' Direccion de Firefox.exe, si se actualiza cambia el nombre de la carpeta'''
        options.binary_location= r'C:\Program Files\WindowsApps\Mozilla.Firefox_105.0.3.0_x64__n80bbvh6b1yt2\VFS\ProgramFiles\Firefox Package Root\firefox.exe' 
        '''Direccion del geckodriver de firefox'''
        driver = webdriver.Firefox(executable_path=r'C:\Users\mauiv\Documents\geckodriver.exe', options=options) 
        '''Direccion de la carpeta donde se guardan los datos'''
        data=pd.read_csv(r'C:\Users\mauiv\Documents\Gmaps\Gmaps\spiders\Final_Data_Hackathon_2022.csv') #Leemos el archivo csv 
        empresasxbuscar=[]
        for i in range(data.shape[0]):
            empresasxbuscar.append(data['NombComp'][i] + ' en ' + data['Estado'][i] + ', ' + data['MunicipioDel'][i] + ', ' + str(data['Colonia'][i]) + ', ' + str(data['Direccion1'][i]) + " " + str(data['Direccion2'][i]))
            #esto es porque con sn al final entiende que quiero saber como llegar
            if empresasxbuscar[i][-3:].upper() == ' SN':
                empresasxbuscar[i] = empresasxbuscar[i][:-3]
        for i in range(len(empresasxbuscar)):
            empresasxbuscar[i] = empresasxbuscar[i].replace('  ', ' ').replace('  ', ' ')
        links_x_rec=[]
        for i in range(len(empresasxbuscar)):
            links_x_rec.append('https://www.google.com/maps/search/' + empresasxbuscar[i].replace(' ', '+'))
        movimiento=ActionChains(driver)
        

        #Damos click a cada elemento/empresa
        for j in range(len(links_x_rec)):
            driver.get(links_x_rec[j])

            if(len(driver.find_elements(By.XPATH, "//a[@class='hfpxzc']"))>0):
                #entramos a la 1er pagina que encontro
                driver.get(driver.find_elements(By.XPATH, "//a[@class='hfpxzc']")[0].get_attribute('href'))
                #Esperamos a que cargue la pagin
                try:
                    WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, "//div[@class='qCHGyb ipilje'][2]")))
                except:
                    pass
                while driver.execute_script("return document.readyState") != "complete":
                    time.sleep(1)
                
                #Si no es empresa nos la saltamos
                if (len(driver.find_elements(By.XPATH, "//button[@jsaction='pane.rating.category']"))==0 and len(driver.find_elements(By.XPATH, "//span/span/span/span/span/span"))==0):
                    continue
            try:
                WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, "//div[@class='qCHGyb ipilje'][2]")))
            except:
                pass
            while driver.execute_script("return document.readyState") != "complete":
                time.sleep(.5)
            
            driver.find_element(By.XPATH, "//h1[@class='DUwDvf fontHeadlineLarge']").click()
            for i in range(2):
                movimiento.send_keys(Keys.DOWN).perform()
    
            if (len(driver.find_elements(By.CSS_SELECTOR, "span.rh7Scc.LaAyid.M5ziBd"))>0):    
                for i in range(3):
                    movimiento.send_keys(Keys.DOWN).perform()
            horas = "" 

            #click a horario
            try:
                driver.find_element(By.CSS_SELECTOR, "span.rh7Scc.LaAyid.M5ziBd").click()
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//tr[@class='y0skZc']/td[1]")))  
                aux3 = driver.find_elements(By.XPATH, "//tr[@class='y0skZc']/td[1]")       
                for l in range(len(aux3)):  
                    if aux3[l].text=="lunes": k= l   
                for l in range(len(aux3)): 
                    horas += aux3[(l+k)%7].text + " " + driver.find_elements(By.XPATH, "//tr[@class='y0skZc']/td[2]")[(l+k)%7].text + ","
                driver.find_element(By.CSS_SELECTOR, "span.rh7Scc.LaAyid.u1oM6").click()
                time.sleep(.1)
            except:
                pass
            for i in range(2):
                movimiento.send_keys(Keys.DOWN).perform()
                time.sleep(.01)

            #Asiganmos los datos a las variables
            GITEM = GmapsItem()
            GITEM["index"]=j
            GITEM["URL"]=links_x_rec[j]
            GITEM["negocio_reclamado"]=True

            GITEM['name'] = driver.find_element(By.XPATH, "//h1[@class='DUwDvf fontHeadlineLarge']/span[@jstcache]").text
            lista=[]
            try:
                GITEM['rating'] = driver.find_element(By.XPATH, "//div[@jsaction='pane.rating.moreReviews']/span/span/span").text
                GITEM['num_reviews'] = driver.find_element(By.XPATH, "//div[@jsaction='pane.rating.moreReviews']/span[2]/span/button").text
                lista=[driver.find_elements(By.XPATH, "//table//tr[@role='img']")[i].get_attribute("aria-label") for i in range(5)]
                GITEM['cant_estrellas'] = [lista[i].replace("\xa0", " ") for i in range(5)]
            
                GITEM["tipo_negocio"]=driver.find_element(By.XPATH, "//button[@jsaction='pane.rating.category']").text
            except:
                pass
            GITEM["horario"] = horas
            #si esta cerrado temporalmente
            if (len(driver.find_elements(By.XPATH, "//img[@src='//maps.gstatic.com/consumer/images/icons/1x/change_history_red600_24dp.png']"))>0):
                GITEM["horario"]= "Cerrado temporalmente/permanente"
            #Para encontrar el lunes pues en maps no siempre esta en el mismo lugar

            try:
                GITEM["latitud"]= driver.current_url.split("/")[6].strip("@").split(",")[0]
                GITEM["longitud"]= driver.current_url.split("/")[6].strip("@").split(",")[1]
            except:
                pass
    
            imagenes = driver.find_elements(By.XPATH, "//img[@class='Liguzb']")
            imagenes = [i.get_attribute("src") for i in imagenes]

            #Esto es porque a veces aparecen imagenes que aparecen al dar clicks para ver mas
            while len(imagenes) != len(driver.find_elements(By.XPATH, "//div[@class='Io6YTe fontBodyMedium']")):
                imagenes.pop(0)

            for i in range (len(imagenes)):
                try:
                    if(imagenes[i]=="https://www.gstatic.com/images/icons/material/system_gm/1x/place_gm_blue_24dp.png"):
                        GITEM["direccion"]= driver.find_elements(By.XPATH, "//div[@class='Io6YTe fontBodyMedium']")[i].text
                        movimiento.send_keys(Keys.DOWN).perform()
                    elif(imagenes[i]=="https://www.google.com/images/cleardot.gif"):
                        GITEM["nota_direccion"] = driver.find_elements(By.XPATH, "//div[@class='Io6YTe fontBodyMedium']")[i].text
                    elif(imagenes[i]=="https://fonts.gstatic.com/s/i/googlematerialicons/event/v14/gm_blue-24dp/1x/gm_event_gm_blue_24dp.png"):
                        try:
                            GITEM["Buscar_Mesa_URL"]= driver.find_element(By.XPATH, "//a[@data-value='Abrir el vínculo de reserva']").get_attribute('href')
                        except:
                            driver.find_element(By.XPATH, "//button[@data-tooltip='Abrir el vínculo de reserva']").click()
                            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='RcCsl fVHpi rXaZJb AG25L']/a[@class='CsEnBe']")))
                            GITEM["Buscar_Mesa_URL"]= [driver.find_elements(By.XPATH, "//a[@class='CsEnBe']")[0].get_attribute('href'), driver.find_elements(By.XPATH, "//a[@class='CsEnBe']")[1].get_attribute('href')]
                            time.sleep(.2)
                            driver.find_element(By.XPATH, "//button[@class='AmPKde']").click()

                    elif(imagenes[i]=="https://www.gstatic.com/images/icons/material/system_gm/1x/public_gm_blue_24dp.png"):
                        try: 
                            GITEM["website"] =driver.find_element(By.XPATH, "//a[@data-tooltip='Abrir el sitio web']").get_attribute('href')
                        except:
                            GITEM["website"] ="www." + driver.find_elements(By.XPATH, "//div[@class='Io6YTe fontBodyMedium']")[i].text
                    elif(imagenes[i]=="https://www.gstatic.com/images/icons/material/system_gm/1x/phone_gm_blue_24dp.png"):
                        GITEM["telefono"] = driver.find_elements(By.XPATH, "//div[@class='Io6YTe fontBodyMedium']")[i].text
                    elif(imagenes[i]=="https://maps.gstatic.com/mapfiles/maps_lite/images/2x/ic_plus_code.png"):
                        GITEM["plus_code"] = driver.find_elements(By.XPATH, "//div[@class='Io6YTe fontBodyMedium']")[i].text
                    elif(imagenes[i]=="https://maps.gstatic.com/consumer/images/icons/1x/send_to_mobile_alt_gm_blue_24dp.png"):
                        #Enviar a celular
                        pass
                    elif(imagenes[i]=="https://www.gstatic.com/images/icons/material/system_gm/1x/local_shipping_gm_blue_24dp.png"):
                        try:
                            GITEM["delivery_url"] = driver.find_element(By.XPATH, "//a[@data-value='Haz un pedido']").get_attribute('href')
                        except:
                            driver.find_elements(By.XPATH, "//div[@class='Io6YTe fontBodyMedium']")[i].click()
                            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//span[@class='BgrMEd i7qH3c cYlvTc']")))
                            GITEM["delivery_url"]= driver.find_element(By.XPATH, "//a[@class='CsEnBe']").get_attribute('href') + ", " + driver.find_elements(By.XPATH, "//a[@class='CsEnBe']")[1].get_attribute('href')
                            time.sleep(.2)
                            driver.find_element(By.XPATH, "//button[@class='AmPKde']").click()

                    elif(imagenes[i]=="https://www.gstatic.com/images/icons/material/system_gm/1x/restaurant_menu_gm_blue_24dp.png"):
                        GITEM["menu"] = driver.find_element(By.XPATH, "//a[@data-item-id='menu']").get_attribute('href')
                    elif(imagenes[i]=="https://www.gstatic.com/images/icons/material/system_gm/1x/verified_user_gm_blue_24dp.png"):
                        GITEM["negocio_reclamado"] = False
                    else:

                        GITEM["Otras"] = driver.find_elements(By.XPATH, "//div[@class='Io6YTe fontBodyMedium']")[i].text
                except:
                    pass
            
            
            #click a las opiniones si hay
            if len(driver.find_elements(By.XPATH, "//button[@class='DkEaL']"))>0 and len(lista)>0:
                webdriver.ActionChains(driver).send_keys(Keys.HOME).perform()
                time.sleep(.3)
                driver.find_elements(By.CSS_SELECTOR, "button.DkEaL")[0].click()
                while driver.execute_script("return document.readyState") != "complete":
                    time.sleep(.5)
                time.sleep(1.5)
                #para guardar las palabras que mas se repiten en las opiniones
                GITEM["opiniones_palabras"] = []
            
                for k in range(len( driver.find_elements(By.XPATH, "//span[@class='bC3Nkc fontBodySmall']"))):
                    GITEM["opiniones_palabras"].append(driver.find_elements(By.XPATH,"//div[@aria-label='Define mejor tus opiniones']//button[@role='radio']")[k+1].text.replace("\n", " "))

                #click a las ordenar por fecha (a veces se queda ahí)
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-value='Ordenar']")))
                    webdriver.ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//button[@data-value='Ordenar']")).click().perform()
                    #funcion que espera en un lugar hasta que se cargue el elemento
                    segs_max=3
                    for i in range(segs_max*40):
                        webdriver.ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//button[@data-value='Ordenar']")).perform()
                        if(len(driver.find_elements(By.XPATH, "//li[@class='fxNQSd'][2]"))>0):
                            break
                        if i==segs_max*10-1:
                            webdriver.ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//button[@data-value='Ordenar']")).click().perform()
                        elif i==segs_max*20-1:
                            webdriver.ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//button[@data-value='Ordenar']")).click().perform()
                        time.sleep(.025)


                    #click a por fecha
                    driver.find_element(By.XPATH, "//li[@class='fxNQSd'][2]").click()
                    time.sleep(1.5)
                except:
                    pass
                try:
                    #Para que cargue to2 los comentarios
                    driver.find_element(By.CSS_SELECTOR, "button.oGrB9e").click()
                    aux=0
                    webdriver.ActionChains(driver).send_keys(Keys.END).perform()
                    time.sleep(.3)
                    webdriver.ActionChains(driver).send_keys(Keys.END).perform()

                    #para cargar los comentarios de hasta abajo    
                    while(len(driver.find_elements(By.XPATH,"//div[@class='DU9Pgb']/span[3]")) != aux and len(driver.find_elements(By.XPATH,"//div[@class='DU9Pgb']/span[3]")) < 40):
                        aux = len(driver.find_elements(By.XPATH,"//div[@class='DU9Pgb']/span[3]"))
                        webdriver.ActionChains(driver).send_keys(Keys.END).perform()
                        time.sleep(.1)
                        driver.find_element(By.CSS_SELECTOR, "button.oGrB9e").click()
                        time.sleep(.2)

                    #dar click para ver toda la opinión
                    aux2=len(driver.find_elements(By.XPATH, "//button[@class='w8nwRe kyuRq']"))
                    while(aux2>0):
                        driver.find_element(By.XPATH, "//button[@class='w8nwRe kyuRq']").click()
                        aux2=aux2-1
                        time.sleep(.1)
                except:
                    pass
                GITEM["opiniones"]=[]
                #Esta parte no falla
                for k in range(len(driver.find_elements(By.XPATH, "//div[@class='MyEned']/span[2]"))):          #estrellas                                                                                                                                                  hace cuanto se escribio la opinion                                          opinion         
                    try:
                        GITEM["opiniones"].append( str(k) + "-:-" + driver.find_elements(By.XPATH, "//div[@class='DU9Pgb']/span[2]")[k].get_attribute("aria-label").replace(" ", "").replace("\xa0estrellas", "").replace(" estrella", "") + "-:-"+ driver.find_elements(By.XPATH, "//div[@class='DU9Pgb']/span[3]")[k].text + "-:-" + driver.find_elements(By.XPATH, "//div[@class='MyEned']/span[2]")[k].text.replace(",", " ") )
                    except:
                        pass
            else:
                pass
            yield GITEM    
        driver.quit() 
        gc.collect()
