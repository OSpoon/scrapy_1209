# -*- coding: utf-8 -*-
import urllib

import scrapy
from PIL import Image
import os

from twisted.python.compat import raw_input


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['douban.com']
    # header信息
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0"
    }

    # 自定义信息，向下层响应(response)传递下去
    customer_data = {'key1': 'value1', 'key2': 'value2'}

    '''重写start_requests，请求登录页面'''
    def start_requests(self):
        print("start_requests")
        resp_url = "https://accounts.douban.com/login"
        return [scrapy.FormRequest(resp_url,
                   headers=self.headers,
                   meta={"cookiejar": 1}, # 表示开启cookie记录，首次请求时写在Request()里
                   callback=self.parse_before_login,
               )]

    def parse_before_login(self, response):
        print("parse_before_login")
        captcha_id = response.xpath('//input[@name="captcha-id"]/@value').extract_first()
        captcha_image_url = response.xpath('//img[@id="captcha_image"]/@src').extract_first()
        if captcha_image_url is None:
            print("登录时无验证码")
            form_data = {'source': 'movie','redir': 'https://movie.douban.com/','form_email': '1825203636@qq.com','form_password': 'zx1234567890', 'remember': 'on','login': '登录'}
        else:
            print("登录时有验证码")
            # 将图片验证码下载到本地
            urllib.request.urlretrieve(captcha_image_url, os.getcwd()+'\output\captcha.jpeg')
            # 打开图片，以便我们识别图中验证码
            try:
                im = Image.open(os.getcwd()+'\output\captcha.jpeg')
                im.show()
                captcha_solution = raw_input('根据打开的图片输入验证码:')
                print('您输入的验证码为 : ',captcha_solution)
                form_data = {'source': 'None',
                             'redir': 'https://www.douban.com',
                             'form_email': '1825203636@qq.com',
                             'form_password': 'zx1234567890',
                             'captcha-solution': captcha_solution,
                             'captcha-id': captcha_id,
                             'remember': 'on',
                             'login': '登录'}
            except Exception as e:
                print(e.message)
        # 表单需要提交的数据
        return scrapy.FormRequest.from_response(response,
                                                meta={"cookiejar": response.meta["cookiejar"]}, #表示使用上一次response的cookie，写在FormRequest.from_response()里post授权
                                                headers=self.headers,formdata=form_data,callback=self.parse_after_login)

    '''登录之后操作'''
    def parse_after_login(self, response):
        print("parse_after_login")
        '''验证登录是否成功'''
        account = response.xpath('//a[@class="bn-more"]/span/text()').extract_first()
        if account is None:
            print("登录失败")
        else:
            print(u"登录成功,当前账户为 %s" % account)

    def parse(self, response):
        # 默认回调函数
        print("默认回调函数")