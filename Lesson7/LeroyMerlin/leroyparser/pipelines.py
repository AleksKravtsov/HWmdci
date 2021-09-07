# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import os
from urllib.parse import urlparse


class LeroyparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.Scrapy_LeroyMerlin

    def process_item(self, item, spider):
        if not item['price']:
            item['price'] = None
        collection = self.mongobase[spider.name]
        collection.update_one({'url': item['url']}, {'$set': item}, upsert=True)
        return item

class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                img = img.replace('w_82,h_82', 'w_2000,h_2000')
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item


    def file_path(self, request, response=None, info=None, *, item=None):
        return f'{item["name"]}/' + os.path.basename(urlparse(request.url).path)