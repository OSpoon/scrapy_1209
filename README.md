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

[TOC]



#### 请求和响应

执行过程 :Request -> 下载器 -> Response

##### 请求对象:

```
scrapy.http.Request（url [，callback，method ='GET'，headers，body，cookies，meta，encoding ='utf-8'，priority = 0，dont_filter = False，errback ] ）
```

| 参数            | 类型        | 描述                                                         |
| --------------- | ----------- | ------------------------------------------------------------ |
| **url**         | 字符串      | 请求的URL                                                    |
| **callback**    | callable    | 将使用此请求的响应（一旦下载）*调用*的函数作为其第一个参数   |
| **method**      | string      | 默认为`'GET'                                                 |
| **meta**        | dict        | [`Request.meta`](https://scrapy-chs.readthedocs.io/zh_CN/0.24/topics/request-response.html#scrapy.http.Request.meta)属性的初始值。如果给定，则此参数中传递的dict将被浅层复制 |
| **body**        | str/unicode | 如果一个 `unicode`被传递，则`str`使用传递的编码（默认为`utf-8`）对其 进行编码。如果 `body`没有给出，则存储空字符串。无论此参数的类型如何，存储的最终值都是`str`（从不 `unicode`或`None`） |
| **headers**     | dict        | dict值可以是字符串（对于单值标头）或列表（对于多值标头）。如果 `None`作为值传递，则根本不会发送HTTP标头 |
| **cookies**     | dict/list   | 使用词典<br />request_with_cookies = Request(url="http://www.example.com", cookies={'currency': 'USD', 'country': 'UY'})<br />
使用列表
request_with_cookies = Request(url="http://www.example.com", cookies=[{'name': 'currency','value': 'USD','domain': 'example.com','path': '/currency'}])<br />
不合并cookie的请求示例:
request_with_cookies = Request(url="http://www.example.com", cookies={'currency': 'USD', 'country': 'UY'},meta={'dont_merge_cookies': True}) |
| **encoding**    | 字符串      | 此请求的编码（默认为`'utf-8'`）。此编码将用于对URL进行百分比编码并将正文转换为`str`（如果给定`unicode`）。 |
| **priority**    | int         | 此请求的优先级（默认为`0`）。调度程序使用优先级来定义用于处理请求的顺序。具有更高优先级值的请求将更早执行。允许使用负值以指示相对较低的优先级。 |
| **dont_filter** | boolean     | 表示调度程序不应过滤此请求。当您想要多次执行相同的请求时，可以使用此选项来忽略重复过滤器。 |
| **errback**     | callable    | 在处理请求时引发任何异常时将*调用*的函数。这包括因404 HTTP错误而失败的页面等。 |

##### 将附加数据传递给回调函数

只回调默认Response

```
示例:parse_page1中回调parse_page2
def parse_page1(self, response):
    return scrapy.Request("http://www.example.com/some_page.html",
                          callback=self.parse_page2)

def parse_page2(self, response):
    # this would log http://www.example.com/some_page.html
    self.log("Visited %s" % response.url)
```

回调多个参数,使用request.meta

```
示例:parse_page1回调parse_page2,回传item参数
def parse_page1(self, response):
    item = MyItem()
    item['main_url'] = response.url
    request = scrapy.Request("http://www.example.com/some_page.html",
                             callback=self.parse_page2)
    request.meta['item'] = item
    return request

def parse_page2(self, response):
    item = response.meta['item']
    item['other_url'] = response.url
    return item
```

##### Request.meta特殊键

cookiejar

单spider多cookie session

```
for i, url in enumerate(urls):
    yield scrapy.Request("http://www.example.com", meta={'cookiejar': i},
        callback=self.parse_page)
```

```
def parse_page(self, response):
    # do some processing
    return scrapy.Request("http://www.example.com/otherpage",
        meta={'cookiejar': response.meta['cookiejar']},
        callback=self.parse_other_page)
```



```
dont_redirect
dont_retry
handle_httpstatus_list
dont_merge_cookies
redirect_urls
bindaddress
```

##### 请求子类FormRequest

```
scrapy.http.FormRequest（url [，formdata，... ] ）
```

| 命令         | 类型               | 描述                                                         |
| ------------ | ------------------ | ------------------------------------------------------------ |
| **formdata** | 元组/dict/iterable | 一个包含HTML表单数据的字典（或（key，value）元组的迭代），它将被url编码并分配给请求的主体 |

##### 构建新FormRequest对象

```
from_response（response [，formname = None，formnumber = 0，formdata = None，formxpath = None，clickdata = None，dont_click = False，... ] ）
```

| 命令           | 类型                                                         | 描述                                                         |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **response**   | （[`Response`](https://scrapy-chs.readthedocs.io/zh_CN/0.24/topics/request-response.html#scrapy.http.Response)object） | 包含HTML表单的响应，该表单将用于预填充表单字段               |
| **formname**   | （*string*）                                                 | 如果给定，将使用name属性设置为此值的表单。                   |
| **formxpath**  | （*string*）                                                 | 如果给定，将使用与xpath匹配的第一个表单。                    |
| **formnumber** | （*整数*）                                                   | 当响应包含多个表单时要使用的表单数。第一个（也是默认值）是`0`。 |
| **formdata**   | （*dict*）                                                   | 要在表单数据中覆盖的字段。如果响应`<form>`元素中已存在某个字段，则该值将被此参数中传递的值覆盖。 |
| **clickdata**  | （*dict*）                                                   | 用于查找单击控件的属性。如果没有给出，将提交表单数据，模拟第一个可点击元素的点击。除了html属性之外，还可以通过属性，通过其相对于表单内其他可提交输入的从零开始的索引来标识控件`nr`。 |
| **dont_click** | （*boolean*）                                                | 如果为True，将提交表单数据而不单击任何元素。                 |

##### 使用FormRequest通过HTTP POST发送数据

```
return [FormRequest(url="http://www.example.com/post/action",
                    formdata={'name': 'John Doe', 'age': '27'},
                    callback=self.after_post)]
```

##### 使用FormRequest.from_response（）模拟方法用户登录

```
import scrapy

class LoginSpider(scrapy.Spider):
    name = 'example.com'
    start_urls = ['http://www.example.com/users/login.php']

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'username': 'john', 'password': 'secret'},
            callback=self.after_login
        )

    def after_login(self, response):
        # check login succeed before going on
        if "authentication failed" in response.body:
            self.log("Login failed", level=scrapy.log.ERROR)
            return

        # continue scraping with authenticated session...
```


scrapyd

scrapyd-deploy 100 -p myspider -v 1

curl http://127.0.0.1:6800/schedule.json -d project=cnblogSpider -d spider=anjuke