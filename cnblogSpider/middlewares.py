# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import requests
from scrapy import signals
from logging import getLogger
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
import time

class SleniumMiddleware(object):

    def __init__(self, timeout=None, service_args=[]):
        print('init start')
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        import os
        project_dir = os.path.abspath(os.path.dirname(__file__))

        self.logger = getLogger(__name__)
        self.timeout = timeout
        self.browser = webdriver.Chrome(executable_path=os.path.join(project_dir,'chromedriver'), chrome_options=chrome_options)
        self.browser.set_window_size(1400, 700)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)
        print('init end')

    def __del__(self):
        print('__del__')
        self.browser.close()

    def process_request(self, request, spider):
        """
        PhantomJS抓取页面
        """
        self.logger.debug("PhantomJS is Starting")
        page = request.meta.get('page', 1)
        print('page => ', page)
        print('url => ', request.url)
        try:
            self.browser.get(request.url)
            if page == 1:
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="pop418"]/a')
                    )
                ).click()
                time.sleep(1)
            input = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="bottomPage"]')
                )
            )
            submit = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="bottom_pager"]/div/a[7]')
                )
            )
            input.clear()
            input.send_keys(page)
            submit.click()
            time.sleep(10)
            return HtmlResponse(url=request.url,
                                body=self.browser.page_source,
                                request=request,
                                encoding='utf-8',
                                status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)

    @classmethod
    def from_crawler(cls, crawler):
        print('from_crawler')
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
                   service_args=crawler.settings.get('PHANTOMJS_SERVICE_ARGS'))


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        proxy_addr = requests.get('http://123.207.35.36:5010/get/').text
        print('代理Ip ：', 'http://{0}'.format(proxy_addr))
        request.meta['proxy'] = 'http://{0}'.format(proxy_addr)


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        from fake_useragent import UserAgent
        ua = UserAgent(verify_ssl=False)
        ua_rendom = ua.random
        print('UserAgent ===> ', ua_rendom)
        request.headers.setdefault('User-Agent', ua_rendom)

class CnblogspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CnblogspiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
