# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import quote


class SuningSpider(scrapy.Spider):
    name = 'suning'
    allowed_domains = ['suning.com']
    base_url = 'https://search.suning.com/'

    def start_requests(self):
        for keyword in self.settings.get('KEYWORD'):
            for page in range(1, self.settings.get('MAX_PAGE') + 1):
                url = self.base_url + quote(keyword) + '/'
                yield scrapy.Request(url=url,
                                     callback=self.parse,
                                     meta={'page': page},
                                     dont_filter=True)

    def parse(self, response):
        print('parse')
        print(response)
        print(response.xpath("//div[@class='title-selling-point']/a/text()").extract())

