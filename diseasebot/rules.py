from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

# in fact, for task: medicine_detail_drugs, no need define rule, so use: dummy_detail_rule
# because for each link, don't need further scrawl, but if no rule defined, the program will get error

rules = {
    'medicine_list_drugs': [
        Rule(LinkExtractor(allow='alpha\/\w*\.html',
                           restrict_xpaths='//nav[1][@aria-label="Drug list navigation by first letter"]//li/a'),
                           callback='parse_item', process_request='copyMetaToNewRequest')
    ],
    'dummy_detail_rule': [
        Rule(LinkExtractor(allow_domains='www.example-test.com'), follow=False,
             callback='parse_item')
    ],
    'disease_list_drugs_mayo': [
        Rule(LinkExtractor(allow='mcd-\w*\.html',
                           restrict_xpaths='//div[@class="ddc-grid"]/div/ul/li/a'),
                           callback='parse_item', process_request='copyMetaToNewRequest')
    ],
}
