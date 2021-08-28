# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from itemloaders.processors import MapCompose, TakeFirst
import scrapy
import re

def get_price(value):
    try:
        return int(value)
    except:
        return value


class LreoymerlinruItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(get_price), output_processor=TakeFirst())
    photos = scrapy.Field()
    article_number = scrapy.Field(output_processor=TakeFirst())
    # specifications = scrapy.Field()


