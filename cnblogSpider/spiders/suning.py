# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import quote

from cnblogSpider.items import SuningItem


class SuningSpider(scrapy.Spider):
    name = 'suning'
    allowed_domains = ['suning.com']
    base_url = 'https://search.suning.com/'
    custom_settings = {
        'ITEM_PIPELINES': {
            'cnblogSpider.pipelines.SuningspiderPipeline': 2,
        }
    }

    def start_requests(self):
        for keyword in self.settings.get('KEYWORD'):
            for page in range(1, self.settings.get('MAX_PAGE') + 1):
                url = self.base_url + quote(keyword) + '/'
                yield scrapy.Request(url=url+'#second-filter',
                                     callback=self.parse,
                                     meta={'page': page},
                                     dont_filter=True)

    def parse(self, response):
        print('parse')
        print()
        titles = response.xpath("//div[@class='title-selling-point']/a/text()").extract()
        while '\n' in titles:
            titles.remove('\n')
        prices = response.xpath("//div[@class='price-box']/span/text()").extract()
        while '\n' in prices:
            prices.remove('\n')
        print(len(titles), titles)
        print(len(prices), prices)
        item = SuningItem()
        item['price'] = prices
        yield item

