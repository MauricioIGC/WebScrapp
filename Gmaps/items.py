# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GmapsItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    direccion = scrapy.Field()
    nota_direccion = scrapy.Field()
    rating = scrapy.Field()
    num_reviews = scrapy.Field()
    cant_estrellas = scrapy.Field()
    temas_reviews = scrapy.Field()
    URL = scrapy.Field()
    Buscar_Mesa_URL = scrapy.Field()
    telefono = scrapy.Field()
    website = scrapy.Field()
    plus_code = scrapy.Field()
    latitud = scrapy.Field()
    longitud = scrapy.Field()
    horario = scrapy.Field()
    horas_punta = scrapy.Field()
    negocio_reclamado = scrapy.Field()
    tipo_negocio = scrapy.Field()
    delivery_url = scrapy.Field()
    menu = scrapy.Field()
    opiniones_palabras = scrapy.Field()
    Otras= scrapy.Field()
    index = scrapy.Field()
    opiniones = scrapy.Field()

    pass

    #Exclusivos del inegi
class INEGItem(scrapy.Item):
    CLEE = scrapy.Field()
    Id = scrapy.Field()
    Nombre = scrapy.Field()
    Razon_social = scrapy.Field()
    Clase_actividad = scrapy.Field()
    Estrato = scrapy.Field()
    Tipo_vialidad = scrapy.Field()
    Calle = scrapy.Field()
    Num_Exterior = scrapy.Field()
    Num_Interior = scrapy.Field()
    Colonia = scrapy.Field()
    CP = scrapy.Field()
    Ubicacion = scrapy.Field()
    Telefono = scrapy.Field()
    Correo_e = scrapy.Field()
    Sitio_internet = scrapy.Field()
    Tipo = scrapy.Field()
    Longitud = scrapy.Field()
    Latitud = scrapy.Field()
    tipo_corredor_industrial = scrapy.Field()
    nom_corredor_industrial = scrapy.Field()
    numero_local = scrapy.Field()

    pass
