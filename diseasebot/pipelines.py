# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector
import datetime
from diseasebot import dbBizUtils
from diseasebot import projectConfig


class DiseasebotPipeline(object):
    def process_item(self, item, spider):
        return item



class MysqlPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(host=crawler.settings.get('MYSQL_HOST'),
                   database=crawler.settings.get('MYSQL_DATABASE'),
                   user=crawler.settings.get('MYSQL_USER'),
                   password=crawler.settings.get('MYSQL_PASSWORD'),
                   port=crawler.settings.get('MYSQL_PORT'))

    def open_spider(self, spider):
        print('----------- open db connection in pipeline')
        self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
        )

    def process_item(self, item, spider):
        # spider medicine list data and store into db
        if projectConfig.isTaskListJob():
            dbBizUtils.insertNewSpiderJobItem(item, self.connection)
        elif projectConfig.isTaskArticleDetailJob():
            dbBizUtils.addOneArticleMedicineOrDisease(projectConfig.getResourceType(), item, self.connection)
            print('---- end request for: %s, time: %s' % (item['source_url'],
                                                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return item

    def close_spider(self, spider):
        print('----------- close db connection in pipeline')
        self.connection.close()
