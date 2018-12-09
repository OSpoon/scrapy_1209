# -*- coding: utf-8 -*-

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from cnblogSpider.spiders.cnblogs import CnblogsSpider
from scrapy.utils.project import get_project_settings

if __name__ == '__main__':
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    runner.crawl(CnblogsSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
