# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class AnjukeSpider(scrapy.Spider):
    name = 'anjuke'
    allowed_domains = ['anjuke.com']
    # start_urls = ['http://anjuke.com/'] # 关闭start_urls
    base_url = "https://bj.zu.anjuke.com"

    '''重写start_requests'''
    def start_requests(self):
        return [scrapy.FormRequest(self.base_url, callback=self.loc_url_callback, dont_filter=True)]


    def loc_url_callback(self, response):
        print(response.xpath("//title/text()").extract()[0])
        loc_list = response.xpath("//div[@class='sub-items sub-level1']/a/@href").extract()
        for loc_url in loc_list:
            print(loc_url)
            yield scrapy.Request(loc_url, callback=self.all_url_callback, dont_filter=True)

    def all_url_callback(self, response):
        print(response.xpath("//title/text()").extract()[0])


    def parse(self, response):
        pass
