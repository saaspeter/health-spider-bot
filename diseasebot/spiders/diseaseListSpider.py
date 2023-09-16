import scrapy
from scrapy import Request

from diseasebot.items import DiseaseItem


class DiseaseListSpider(scrapy.Spider):
    name = "diseaseList"
    allowed_domains = ['drugs.com']
    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'LOG_ENABLED': True,
        'LOG_STDOUT': True
    }
    level = 1

    list_url_root = 'https://www.drugs.com/health-guide-'
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    def start_requests(self):

        for i in self.alphabet:
            url = self.list_url_root + str(i) + '1' + '.html'
            yield scrapy.Request(url=url, callback=self.parse, meta={'level': self.level})

    def parse(self, response):
        # print(response.text)
        ulNode = response.css('.contentBox ul')
        diseaseNamelist = ulNode[0].css('li a') if ulNode else []
        item = DiseaseItem()
        for diseaseName in diseaseNamelist:
            item['name'] = diseaseName.css('::text')[0].extract()
            link = diseaseName.css('::attr(href)')[0].extract()
            item['link'] = link.split('ref=')[0]
            print(item['name']+':'+link)
            yield item
                # yield scrapy.Request(url=item['link'], callback=self.parse, meta=response.meta)





