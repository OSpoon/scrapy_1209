# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
import os
from pymongo import MongoClient

base_dir = os.getcwd()

class MongoPipeline(object):
    # 实现保存到mongo数据库的类，
    collection = 'ftx'  # mongo 数据库的 collection 的默认名字

    def __init__(self, mongo_uri, db_name, db_user, db_pass):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass

    @classmethod
    def from_crawler(cls, crawler):
        # scrapy 为我们访问settings提供了这样的一个方法，这里，
        # 我们需要从 settings.py 文件中，取得数据库的URI和数据库名称
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            db_name=crawler.settings.get('DB_NAME'),
            db_user=crawler.settings.get('DB_USER'),
            db_pass=crawler.settings.get('DB_PASS'))

    def open_spider(self, spider):  # 爬虫启动时调用，连接到数据库
        self.client = MongoClient(self.mongo_uri)
        self.zfdb = self.client[self.db_name]
        self.zfdb.authenticate(self.db_user, self.db_pass)
        print('连接到数据库')

    def close_spider(self, spider):  # 爬虫关闭时调用，关闭数据库连接
        self.client.close()

    def process_item(self, item, spider):
        # if item["region"]:
        print('process_item')
        self.collection = item["region"]
        if item["region"] == "不限":
            item["region"] = item["address"][0:2]
        self.zfdb[self.collection].insert({
            "title": item["title"].strip(),
            "rooms": item["rooms"],
            "area": item["area"],
            "price": item["price"],
            "address": item["address"],
            "traffic": item["traffic"],
            "region": item["region"],
            "direction": item["direction"],
        })
        return item

class CnblogspiderPipeline(object):

    def __init__(self):
        self.file = open('output/pagers.json', 'w')

    def process_item(self, item, spider):
        if item['title']:
            line = json.dumps(dict(item)) + '\n'
            self.file.write(line)
            return item
        else:
            raise DropItem("Missing title in %s" % item)

class ImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item