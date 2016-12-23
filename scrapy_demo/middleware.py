# -*- coding: utf-8 -*-
import logging
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class SeleniumMiddleware(object):
    def __init__(self):
        logger.debug("init SeleniumMiddleware, starting driver.")
        self.driver = webdriver.PhantomJS()

    def __del__(self):
        logger.debug("destruct SeleniumMiddleware, closing driver.")
        self.driver.close()

    def process_request(self, request, spider):
        if not request.meta.get('enable_js', False):  # only render page which enable_js is True
            return

        try:
            self.driver.set_page_load_timeout(3)
            self.driver.get(request.url)
            return HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8', request=request)
        except TimeoutException:
            logger.warning("phantomjs load %(url)s timeout! use incompleted page source.", {'url': request.url})
            return HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8', request=request)
        finally:
            # driver.close()
            pass
