# -*- coding: utf-8 -*-
import scrapy

from cnblogSpider.items import DoutulaspiderItem


class DoutulaSpider(scrapy.Spider):

    name = 'doutula'
    allowed_domains = ['doutula.com']
    # start_urls = ['http://doutula.com/']
    baseUrl = "http://doutula.com"

    # 开启数据保存&图片下载管道
    custom_settings = {
        'ITEM_PIPELINES': {
            'cnblogSpider.pipelines.DoutulaPipeline': 300,
            'cnblogSpider.pipelines.ImagesPipeline': 400,
        }
    }

    #重写start_requests
    def start_requests(self):
        start_url = self.baseUrl
        return [scrapy.FormRequest(start_url,
                                   callback=self.item_url_callback,
                                   dont_filter=True)]

    # 解析item，获取详情页面
    def item_url_callback(self, response):
        loc_list = response.xpath("//div[@class='col-sm-9']/a/@href").extract()
        for loc_url in loc_list:
            print(loc_url)
            yield scrapy.Request(loc_url, callback=self.parse, dont_filter=True)
        next_page = response.xpath("//div[@class='text-center']/ul/li/a/@href").extract()
        if len(next_page) > 0:
            next_page = next_page[-1]
            if next_page:
                next_page = self.baseUrl+next_page
                print('下一页地址：', next_page)
                yield scrapy.Request(next_page,
                                     callback=self.item_url_callback,
                                     dont_filter=True)

    # 解析页面数据，获取信息
    def parse(self, response):
        item = DoutulaspiderItem()
        item['title'] = response.xpath("//div[@class='pic-title']/h1/a/text()").extract()[0]
        item['update'] = response.xpath("//div[@class='pic-title']/div/span/text()").extract()[0]
        images = response.xpath("//div[@class='pic-content']/div/table/tbody/tr/td/a/img/@src").extract()
        item['image_urls'] = images
        # 交由管道处理（完成数据Mongo存储，图像下载）
        yield item
