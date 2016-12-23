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
    keywords = [
        '华为荣耀畅玩4X',
        '苹果iPhone6',
        '苹果iPhone6Plus',
        '苹果iPhone6s',
        '华为 - F202',
        '小米红米Note',
        '华为AscendP8',
        '锋达通 - C800 +',
        '海信M20 - T',
        '欧珀R9M',
        '百合 - C20',
        '华为荣耀畅玩4X（Che - CL10）',
        '天元 - CT - S200(政企)',
        '小米红米2',
        '百合 - C20M',
        '步步高Y51A',
        'SAMSUNG - B309',
        '华为Mate7',
        '老来宝 - 620V',
        '比酷 - A181',
        '华为荣耀4A',
        '苹果iPhone6sPlus',
        '步步高X7',
        '海信 - M30(4G)',
        '全盈 - E6',
        '欧珀R7sm',
        '华为Huawei',
        'RIO - AL00',
        '酷派5263S高配',
        '联想A2580',
        '欧珀R7c',
        '华为荣耀畅玩4C',
        '中兴 - 远航MINI - A601',
        '酷派5263'
    ]

    def start_requests(self):
        for word in self.keywords:
            query = {'wd': word, 'pn': '00', 'tn': 'baidurt', 'ie': 'utf-8', 'bsst': '1'}
            query_str = urllib.urlencode(query)
            url = 'http://www.baidu.com/s' + '?' + query_str
            yield self.make_requests_from_url(url)

    def parse(self, response):
        keyword = self._parse_keyword(response.url)
        le = LinkExtractor(allow=r'http://detail.zol.com.cn/cell_phone/.*')
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
    # df = pd.read_csv("e:/imsimdn.csv").iloc[:,0].drop_duplicates
    process = CrawlerProcess()
    process.crawl(BaiduSearchSpider)
    process.start()
