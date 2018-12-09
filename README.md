### Scrapy爬虫框架

简述：

​	Scrapy中的各大组件

​	Scrapy引擎

​	Scheduler调度器

​	Downloader下载器

​	Spider负责获取页面

​	Item Pipelin负责持久化

安装命令：pip install Scrapy

创建项目：scrapy startproject cnblogSpider

创建爬虫：scrapy genspider cnblogs "cnblogs.com"

执行爬虫：scrapy crawl cnblogs

​		 scrapy crawl cnblogs -o papers.cvs