# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from diseasebot import projectConfig
from diseasebot import urls
from diseasebot.rules import rules
from diseasebot.items import *
from diseasebot.loaders import *
from scrapy.http import Request
from diseasebot import utils


class UniversalSpider(CrawlSpider):

    name = 'universal'
    
    def __init__(self, name, *args, **kwargs):
        config = projectConfig.custom_setting
        self.config = config
        self.rules = rules.get(config.get('rules'))
        start_urls = config.get('start_urls')
        if start_urls:
            if start_urls.get('type') == 'static':
                self.start_urls = start_urls.get('value')
            elif start_urls.get('type') == 'dynamic':
                self.start_urls = list(eval('urls.' + start_urls.get('method'))(*start_urls.get('args', [])))

        self.allowed_domains = config.get('allowed_domains')
        # CrawlSpider(UniversalSpider, self).__init__(*args, **kwargs)
        super().__init__(self, *args, **kwargs)
        # CrawlSpider(UniversalSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        start_requests_config = self.config.get('start_requests')
        if start_requests_config:
            request_list = list(eval('urls.' + start_requests_config.get('method'))(*start_requests_config.get('args', [])))
            for req in request_list:
                yield req
        elif self.start_urls:
            yield from super().start_requests()

    # if no need further scrawl, so no valid rule, then will call this method
    def parse_start_url(self, response, **kwargs):
        return self.parse_item(response)

    def parse_item(self, response):
        itemConfig = self.config.get('item')
        if itemConfig:
            cls = eval(itemConfig.get('class'))()
            loader = eval(itemConfig.get('loader'))(cls, response=response)
            # 动态获取属性配置
            for key, value in itemConfig.get('attrs').items():
                for extractor in value:
                    if extractor.get('method') == 'xpath' and not extractor.get('after_load'):
                        loader.add_xpath(key, *extractor.get('args'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'css' and not extractor.get('after_load'):
                        loader.add_css(key, *extractor.get('args'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'value' and not extractor.get('after_load'):
                        loader.add_value(key, *extractor.get('args'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'attr' and not extractor.get('after_load'):
                        loader.add_value(key, getattr(response, *extractor.get('args')))
                    if extractor.get('method') == 'request.meta' and not extractor.get('after_load'):
                        loader.add_value(key, response.meta.get(utils.getRequestMetaCustomKey(extractor.get('key'))))
            item = loader.load_item()
            # after load, call some post handler
            for key, value in itemConfig.get('attrs').items():
                for extractor in value:
                    if extractor.get('method') == 'deleteHtmlNode' and extractor.get('after_load'):
                        utils.deleteHtmlNode(item, key, *extractor.get('args'))
                    if extractor.get('method') == 'extractNameTemp' and extractor.get('after_load'):
                        utils.extractNameTemp(item, key, *extractor.get('args'))

            if response.status != 200:
                print('error: request scrawl failed, url is: '+response.url+'response status is:'
                      + response.status+' , body:'+response.body)

            yield item


    # don't delete this method, this is used in urls.py for process_request fun
    def copyMetaToNewRequest(self, request, response):
        if response.meta:
            for key in response.meta:
                if str(key).startswith(projectConfig.REQUEST_META_PREFIX) and not request.meta.get(key):
                    request.meta[key] = response.meta.get(key)
        return request
