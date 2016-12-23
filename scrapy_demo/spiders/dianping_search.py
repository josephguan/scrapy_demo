# -*- coding: utf-8 -*-
import urllib
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exporters import CsvItemExporter
from scrapy.linkextractors import LinkExtractor
from scrapy import signals
import re

##################################################################
from scrapy.loader import ItemLoader
from scrapy_demo.middleware import SeleniumMiddleware


class DianpingSearchSpider(scrapy.Spider):
    """大众点评列表/搜索爬虫

    爬取大众点评的列表或搜索结果。
    """

    name = u"dianping_search"
    allowed_domains = [u"dianping.com"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy_demo.spiders.dianping_search.CleanupListPipeline': 300,
            'scrapy_demo.spiders.dianping_search.ToStringPipeline': 350,
            'scrapy_demo.spiders.dianping_search.DianpingSearchPipeline': 380,
            'scrapy_demo.spiders.dianping_search.CSVWriterPipeline': 400,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 350,
            'scrapy_demo.middleware.SeleniumMiddleware': 600,
        },
        'DOWNLOAD_DELAY': 5,
        # 'AJAXCRAWL_ENABLED': True,
        'USER_AGENT': u'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
    }

    start_urls = ["http://www.dianping.com/search/category/7/10/g110r31", ]

    def parse(self, response):
        helper_links = LinkExtractor(restrict_xpaths="""//div[@class="page"]""")
        content_links = LinkExtractor(restrict_xpaths="""//div[@id="shop-all-list"]//a[@data-hippo-type="shop"]""")

        for content in content_links.extract_links(response):
            yield scrapy.Request(content.url, callback=self.parse_content, meta={'enable_js': True})

        for helper in helper_links.extract_links(response):
            yield scrapy.Request(helper.url)

    def parse_content(self, response):
        item = ItemLoader(item=DianpingSearchItem(), response=response)

        item.add_value("shop_id", response.url)
        item.add_xpath("name", """//h1[@class="shop-name"]/text()""")
        item.add_xpath("category", """//*[@class="breadcrumb"]/a/text()""")

        item.add_xpath("level", """//*[@class="brief-info"]/span[1]/@title""")
        item.add_xpath("comments", """//*[@class="brief-info"]/span[2]/text()""")
        item.add_xpath("price", """//*[@class="brief-info"]/span[3]/text()""")
        item.add_xpath("taste_level", """//*[@class="brief-info"]/span[4]/text()""")
        item.add_xpath("env_level", """//*[@class="brief-info"]/span[5]/text()""")
        item.add_xpath("service_level", """//*[@class="brief-info"]/span[6]/text()""")

        item.add_xpath("address", """//*[contains(@class,"address")]/span[2]/text()""")
        item.add_xpath("open_time", """//*[@id="basic-info"]/div[3]/p[1]/span[2]/text()""")
        item.add_xpath("tags", """//*[@id="comment"]/div[1]/div[2]//a/text()""")

        item.add_xpath("lat", """//*[@id="map"]/img/@src""")
        item.add_xpath("lon", """//*[@id="map"]/img/@src""")
        yield item.load_item()


##################################################################
# Item Definition
##################################################################
class DianpingSearchItem(scrapy.Item):
    shop_id = scrapy.Field()
    name = scrapy.Field()
    category = scrapy.Field()
    level = scrapy.Field()
    comments = scrapy.Field()
    price = scrapy.Field()
    taste_level = scrapy.Field()
    env_level = scrapy.Field()
    service_level = scrapy.Field()
    address = scrapy.Field()
    open_time = scrapy.Field()
    tags = scrapy.Field()
    lat = scrapy.Field()
    lon = scrapy.Field()


##################################################################
# Pipeline Definition
##################################################################
class DianpingSearchPipeline(object):
    def __init__(self):
        self.latlon_p = re.compile(r'.*center=(.*?),(.*?)&.*')
        self.shopid_p = re.compile(r'.*/shop/(\d+).*')
        self.num_p = re.compile(r'.*?([0-9.]+).*')

    def process_item(self, item, spider):
        # get lat and lon
        latlon_m = self.latlon_p.match(item['lat'])
        if latlon_m:
            item['lat'] = latlon_m.group(1)
            item['lon'] = latlon_m.group(2)

        # get shop id
        shopid_m = self.shopid_p.match(item['shop_id'])
        if shopid_m:
            item['shop_id'] = shopid_m.group(1)

        # get number from item fields
        item['env_level'] = self._get_num(item['env_level'])
        item['service_level'] = self._get_num(item['service_level'])
        item['taste_level'] = self._get_num(item['taste_level'])
        item['price'] = self._get_num(item['price'])

        return item

    def _get_num(self, text, when_fail=''):
        num_m = self.num_p.match(text)
        if num_m:
            return num_m.group(1)
        return when_fail


class CleanupListPipeline(object):
    def process_item(self, item, spider):
        for k, v in item.iteritems():
            item[k] = [x.strip() for x in v if x.strip() != ""]
        return item


class ToStringPipeline(object):
    def process_item(self, item, spider):
        for k, v in item.iteritems():
            item[k] = "|".join(v)
        return item


class CSVWriterPipeline(object):
    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file = open('%s_result.csv' % spider.name, 'w+b')
        self.files[spider] = file
        # kwargs = {'fields_to_export': ['key', 'type', 'title', 'link']}
        # self.exporter = CsvItemExporter(file, True, "|", **kwargs)
        self.exporter = CsvItemExporter(file, True, "|", )
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        print "export item"
        for k, v in item.iteritems():
            print k, v

        self.exporter.export_item(item)
        return item

    def get_title(self, titles):
        for title in titles:
            if (title.strip() != ''):
                return title.strip().__str__()


##################################################################
if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(DianpingSearchSpider)
    process.start()
