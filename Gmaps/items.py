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
    scrap_sel = scrapy.Field()
    opiniones = scrapy.Field()
    pass
