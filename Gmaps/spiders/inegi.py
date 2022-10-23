

from Gmaps.items import INEGItem

import json
import scrapy

class InegiSpider(scrapy.Spider):

    name = 'inegi'

    allowed_domains = ['www.inegi.org.mx']

    start_urls = ['http://www.inegi.org.mx/']

    

    def parse(self, response):
        data=pd.read_csv(r'C:\Users\mauiv\Documents\Gmaps\Gmaps\spiders\Final_Data_Hackathon_2022.csv', index_col=0) #Leemos el archivo csv 
        municipios=pd.read_csv(r'C:\Users\mauiv\Documents\Gmaps\Gmaps\spiders\municipios.csv', index_col=0) #Leemos el archivo csv que contiene claves de municipios y EF de México

        for k in range(data.shape[0]): #Recorremos el archivo csv
            aux1, aux2="",""
            for i in range(municipios.shape[0]):
                if data.iloc[k,-2]==municipios.iloc[i,1] and data.iloc[k,2]==municipios.iloc[i,4]:
                    aux1=str(municipios.iloc[i,0])
                    aux2=str(municipios.iloc[i,3])
                    break
                else:
                    if data.iloc[k,-2]==municipios.iloc[i,1]:
                        aux1=str(municipios.iloc[i,0])
                        if data.iloc[k,-2]!=data.iloc[k+1,-2]:
                            aux2="0"
                            break
                        
            aux3=data['NombComp'][i].replace(" ", ",").replace(",,", ",") 
            aux='https://www.inegi.org.mx/app/api/denue/v1/consulta/BuscarAreaActEstr/'+ aux1 +'/'+ aux2 +'/0/0/0/0/0/0/0/'+ aux3 +'/1/5/0/0/379ba5ea-3170-423d-a147-3f9533b74d49
            yield scrapy.Request(aux, callback=self.parse_inegi,
                                    meta={'item': INEGItem(CLEE=data['CLEE'][i], Id=data['Id'][i], Nombre=data['Nombre'][i], Razon_social=data['Razon_social'][i], Clase_actividad=data['Clase_actividad'][i], Estrato=data['Estrato'][i], Tipo_vialidad=data['Tipo_vialidad'][i], Calle=data['Calle'][i], Num_Exterior=data['Num_Exterior'][i],
                                        Num_Interior=data['Num_Interior'][i], Colonia=data['Colonia'][i], CP=data['CP'][i], Ubicacion=data['Ubicacion'][i], Telefono=data['Telefono'][i], Correo_e=data['Correo_e'][i], Sitio_internet=data['Sitio_internet'][i], Tipo=data['Tipo'][i], Longitud=data['Longitud'][i], Latitud=data['Latitud'][i], 
                                        tipo_corredor_industrial=data['tipo_corredor_industrial'][i], nom_corredor_industrial=data['nom_corredor_industrial'][i], numero_local=data['numero_local'][i])})

            
            