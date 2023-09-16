# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item
from diseasebot import projectConfig
from diseasebot import utils


class BaseItem(Item):
    response_status = Field()
    response_body = Field()

    def IsResponseSuccess(self):
        return True if str(self["response_status"]) == '200' else False

class MedicineListPageItem(BaseItem):
    # medicine name list from site page, e.g: for drugs.com site, it is the <a> medicine list
    medicine_list_page = Field()
    source_sitetag = Field()

    def getItemsList(self):
        itemList = []
        website = projectConfig.getWebSite()
        language = projectConfig.getLanguageSite()
        if self['medicine_list_page']:
            for x in self['medicine_list_page']:
                item = MedicineItem()
                item['name'] = utils.getMedicineNameFromListPageNode(website, x)
                item['source_url'] = utils.getMedicineLinkFromListPageNode(website, x)
                item['site_url'] = website
                item['source_sitetag'] = self['source_sitetag']
                item['job_id'] = projectConfig.JobId
                item['language'] = language
                itemList.append(item)

        return itemList


class MedicineItem(BaseItem):
    # type = 'MedicineItem'
    name = Field()
    name_temp = Field() # extract the name_temp node for further hanlding, not store db
    name_general = Field()
    name_brand = Field()
    is_general = Field()
    source_url = Field()
    site_url = Field()
    source_sitetag = Field()
    language = Field()
    job_id = Field()
    spider_log = Field()
    resource_type = Field()
    full_article = Field()

class DiseaseListPageItem(BaseItem):
    # Disease name list from site page, e.g: for drugs.com site, it is the <a> Disease list
    disease_list_page = Field()
    source_sitetag = Field()

    def getItemsList(self):
        itemList = []
        website = projectConfig.getWebSite()
        language = projectConfig.getLanguageSite()
        if self['disease_list_page']:
            for x in self['disease_list_page']:
                item = DiseaseItem()
                item['name'] = utils.getDiseaseNameFromListPageNode(website, x)
                item['source_url'] = utils.getDiseaseLinkFromListPageNode(website, x)
                item['site_url'] = website
                item['source_sitetag'] = self['source_sitetag']
                item['job_id'] = projectConfig.JobId
                item['language'] = language
                itemList.append(item)

        return itemList


class DiseaseItem(BaseItem):
    # define the fields for your item here like:
    name = Field()
    source_url = Field()
    site_url = Field()
    source_sitetag = Field()
    language = Field()
    job_id = Field()
    spider_log = Field()
    resource_type = Field()
    full_article = Field()
