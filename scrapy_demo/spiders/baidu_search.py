# -*- coding: utf-8 -*-
import urllib
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor


##################################################################
class BaiduSearchSpider(scrapy.Spider):
    """百度搜索爬虫

    根据关键字（非规则化的终端的名字），在百度中搜索，从搜索结果中提取
    这个终端在zol上的对应地址，以便获取这个终端的标准名字。
    """

    name = "baidu_search"
    allowed_domains = []
    start_urls = ()
    custom_settings = {'ITEM_PIPELINES': {'scrapy_demo.spiders.baidu_search.BaiduSearchItemPipeline': 300}}

    # 搜索的关键字
    keywords = ['iphone6s', 'ip 6s', '苹果6s', '天机7', '荣耀6']

    def start_requests(self):
        for word in self.keywords:
            query = {'wd': word + " zol", 'pn': '00', 'tn': 'baidurt', 'ie': 'utf-8', 'bsst': '1'}
            query_str = urllib.urlencode(query)
            url = 'http://www.baidu.com/s' + '?' + query_str
            yield self.make_requests_from_url(url)

    def parse(self, response):
        keyword = self._parse_keyword(response.url)
        le = LinkExtractor(allow=r'http://detail.zol.com.cn/cell_phone.*')
        for link in le.extract_links(response):
            item = BaiduSearchItem()
            item['keyword'] = keyword
            item['link'] = link.url
            item['name'] = link.text
            yield item

    def _parse_keyword(self, url):
        unquoted_url = urllib.unquote(url)
        query_str = urllib.splitquery(unquoted_url)[1]
        wd = filter(lambda x: x.startswith("wd="), query_str.split("&"))
        if wd is not None:
            return wd[0].split("=")[1]


##################################################################
class BaiduSearchItem(scrapy.Item):
    """百度搜索结果

    """
    keyword = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()


##################################################################
class BaiduSearchItemPipeline(object):
    """输出百度搜索结果

    """

    def process_item(self, item, spider):
        print '---------- search result ------------'
        print item['keyword']
        print item['link']
        print item['name']


##################################################################
if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(BaiduSearchSpider)
    process.start()
