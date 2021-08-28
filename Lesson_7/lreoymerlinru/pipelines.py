# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.pipelines.images import ImagesPipeline
import scrapy
from pymongo import MongoClient
import pathlib as ph

class LreoymerlinruPipeline:
    def process_item(self, item, spider):
        return item

# Здесь только обработка фото
class LreoymerlinruPhotosPipeline(ImagesPipeline):

    def __init__(self):
        super.__init__()
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlen

    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                # scrapy может пропустить ошибку и не скачать
                try:  # Разрыв сессии
                    yield scrapy.Request(img)
                except Exception as err:
                    print(err)
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        """Переопределяем путь для сохраняемого изображения"""
        path = ph.Path(request.url)
        image_name = path.name
        return f"{item['name']} ({item['article_number']})/{image_name}"

    def item_completed(self, results, item, info):
        return item

    def process_item(self, item, spider):
        """Кладем в БД"""
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
