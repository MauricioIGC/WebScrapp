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
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import gc

class EmpresaSpider(scrapy.Spider):
    name = 'empresa'
    start_urls = ['https://www.google.com/maps/search/restaurante+en+Álvaro+Obregón']

    # Usando un dummy ficticio para scrapy request
    def start_requests(self):
        url = "https://www.google.com/maps/search/restaurante+en+Álvaro+Obregón"
        yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        #Iniciamos el webdriver
        options = webdriver.firefox.options.Options()
        options.headless = False
        options.binary_location= r'C:\Program Files\WindowsApps\Mozilla.Firefox_105.0.3.0_x64__n80bbvh6b1yt2\VFS\ProgramFiles\Firefox Package Root\firefox.exe' # Direccion de Firefox.exe, si se actualiza cambia el nombre de la carpeta
        driver = webdriver.Firefox(executable_path=r'C:\Users\mauiv\Documents\geckodriver.exe', options=options) #Direccion de geckodriver.exe
        driver.get("https://www.google.com/maps/search/restaurante+en+Álvaro+Obregón")
        #Esperamos a que cargue la pagina
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.hfpxzc")))
        #Para que cargue la pagina
        #monitoreamos el estado de document.readyState
        #si es complete, significa que la pagina ya cargo
        #si no, esperamos 1 segundo y volvemos a monitorear
        while driver.execute_script("return document.readyState") != "complete":
            time.sleep(1)
        

        

        #Esta parte sirve para cargar todos los elementos de la página
        
        time.sleep(.2)
        driver.find_elements(By.CSS_SELECTOR, "div.TFQHme")[-2].click()
        movimiento=ActionChains(driver)

        for i in range(1):
            movimiento.send_keys(Keys.END).perform()
            time.sleep(random.uniform(.5, 2))
        #función que guarda todos los links 
        def get_links(fdriver):
            links=[]
            for i in range(len(fdriver)):
                links.append(fdriver[i].get_attribute("href"))
            return links
        links_x_rec=get_links(driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc"))



        #Damos click a cada elemento/empresa
        for j in range(len(links_x_rec)):
            driver.get(links_x_rec[j])
            while driver.execute_script("return document.readyState") != "complete":
                time.sleep(1)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class='qCHGyb ipilje'][2]")))
            
            driver.find_element(By.XPATH, "//h1[@class='DUwDvf fontHeadlineLarge']").click()
            for i in range(5):
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
                time.sleep(.2)
                driver.find_element(By.CSS_SELECTOR, "span.rh7Scc.LaAyid.u1oM6").click()
            except:
                pass
            for i in range(3):
                movimiento.send_keys(Keys.DOWN).perform()
                time.sleep(.01)

            #Asiganmos los datos a las variables
            GITEM = GmapsItem()
            GITEM["index"]=j
            GITEM["URL"]=links_x_rec[j]

            GITEM['name'] = driver.find_element(By.XPATH, "//h1[@class='DUwDvf fontHeadlineLarge']/span[@jstcache]").text
            GITEM['rating'] = driver.find_element(By.XPATH, "//div[@jsaction='pane.rating.moreReviews']/span/span/span").text
            GITEM['num_reviews'] = driver.find_element(By.XPATH, "//div[@jsaction='pane.rating.moreReviews']/span[2]/span/button").text
            lista=[driver.find_elements(By.XPATH, "//table//tr[@role='img']")[i].get_attribute("aria-label") for i in range(5)]
            GITEM['cant_estrellas'] = [lista[i].replace("\xa0", " ") for i in range(5)]
            GITEM["negocio_reclamado"]=True
            GITEM["tipo_negocio"]=driver.find_element(By.XPATH, "//button[@jsaction='pane.rating.category']").text
            GITEM["horario"] = horas
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
            GITEM["scrap_sel"]="Selenium"
            
            GITEM["opiniones_palabras"] = []
    
            #Para que cargue lo de hasta abajo
            for i in range(30):
                movimiento.send_keys(Keys.DOWN).perform()
                time.sleep(.01)

            #click a + palabras que describen el lugar
            if len(driver.find_elements(By.XPATH, "//div[@aria-label='Define mejor tus opiniones']//button[@role='radio']"))>5:
                driver.find_elements(By.XPATH, "//div[@class='e2moi']//button")[-1].click()
            else:
                pass
            
            for k in range(len( driver.find_elements(By.XPATH, "//span[@class='bC3Nkc fontBodySmall']"))):
                GITEM["opiniones_palabras"].append(driver.find_elements(By.XPATH,"//div[@aria-label='Define mejor tus opiniones']//button[@role='radio']")[k+1].text.replace("\n", " "))

            
            
            #click a las opiniones si hay
            if len(driver.find_elements(By.XPATH, "//button[@class='DkEaL']"))>0:
                #click a las opiniones
                
                driver.find_elements(By.CSS_SELECTOR, "button.DkEaL")[0].click()
                while driver.execute_script("return document.readyState") != "complete":
                    time.sleep(.5)
                #click a las ordenar po
                time.sleep(.8)
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
                time.sleep(.8)
                #Para que cargue to2 los comentarios
                driver.find_element(By.CSS_SELECTOR, "button.oGrB9e").click()
                aux=0
                webdriver.ActionChains(driver).send_keys(Keys.END).perform()
                time.sleep(.3)
                webdriver.ActionChains(driver).send_keys(Keys.END).perform()

                #click a los comentarios que sean muy largos y no se puedan ver    
                while(len(driver.find_elements(By.XPATH,"//div[@class='DU9Pgb']/span[3]")) != aux and len(driver.find_elements(By.XPATH,"//div[@class='DU9Pgb']/span[3]")) < 30):
                    aux = len(driver.find_elements(By.XPATH,"//div[@class='DU9Pgb']/span[3]"))
                    webdriver.ActionChains(driver).send_keys(Keys.END).perform()
                    time.sleep(.2)
                    driver.find_element(By.CSS_SELECTOR, "button.oGrB9e").click()
                    time.sleep(.3)

                #dar click para ver toda la opinión
                aux2=len(driver.find_elements(By.XPATH, "//button[@class='w8nwRe kyuRq']"))
                while(aux2>0):
                    driver.find_element(By.XPATH, "//button[@class='w8nwRe kyuRq']").click()
                    aux2=aux2-1
                    time.sleep(.2)
                GITEM["opiniones"]=[]
                #Esta parte no falla
                for k in range(len(driver.find_elements(By.XPATH, "//div[@class='MyEned']/span[2]"))):          #estrellas                                                                                                                                                  hace cuanto se escribio la opinion                                          opinion         
                    GITEM["opiniones"].append( str(k) + "-:-" + driver.find_elements(By.XPATH, "//div[@class='DU9Pgb']/span[2]")[k].get_attribute("aria-label").replace(" ", "").replace("\xa0estrellas", "").replace(" estrella", "") + "-:-"+ driver.find_elements(By.XPATH, "//div[@class='DU9Pgb']/span[3]")[k].text + "-:-" + driver.find_elements(By.XPATH, "//div[@class='MyEned']/span[2]")[k].text.replace(",", " ") )
            else:
                pass
            yield GITEM    
        #driver.quit()
        gc.collect()
