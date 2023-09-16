from diseasebot import urls
import json
from scrapy import Selector
import mysql.connector
from diseasebot.items import *

# for mysql db ops: see: https://www.w3schools.com/python/python_mysql_select.asp
# https://www.geeksforgeeks.org/python-mysql/

# insert into table:kh_spider_job_items for further spider item details
def insertNewSpiderJobItem(pageItem, db_connection):
    """insert table kh_spider_job_items"""
    resource_type = projectConfig.RESOURCE_TYPE_MEDICINE
    if isinstance(pageItem, MedicineListPageItem):
        resource_type = projectConfig.RESOURCE_TYPE_MEDICINE
    elif isinstance(pageItem, DiseaseListPageItem):
        resource_type = projectConfig.RESOURCE_TYPE_DISEASE
    else:
        raise ValueError('item should be a MedicineListPageItem or DiseaseListPageItem, please check code')

    sqlTemplate = 'insert into kh_spider_job_items (resource_type, name, source_url, ' \
                  'site_url, source_sitetag, language, status, job_id) select %s, %s, %s, %s, %s, %s, %s, %s from dual' \
                  ' where not exists (select 1 from kh_spider_job_items where source_url=%s and job_id=%s)'

    cursor = db_connection.cursor()
    itemList = pageItem.getItemsList()
    status = 1
    for medicineItem in itemList:
        if medicineItem:
            values = (resource_type, medicineItem.get("name"),
                      medicineItem.get("source_url"), medicineItem.get("site_url"),
                      medicineItem.get("source_sitetag"), medicineItem.get("language"),
                      status, medicineItem.get("job_id"), medicineItem.get("source_url"),
                      medicineItem.get("job_id"))
            cursor.execute(sqlTemplate, values)

    db_connection.commit()


def insertNewSpiderJob(db_connection, site_url, resource_type, source_sitetag):
    if not db_connection or not site_url or not resource_type:
        raise ValueError('parameters is empty in insertNewSpiderJob')
    sql = 'insert into kh_spider_job (site_url, resource_type, source_sitetag, status_list, status_detail, start_time_list)' \
          ' values (%s, %s, %s, %s, %s, now())'
    values = (site_url, resource_type, source_sitetag, projectConfig.JOB_STATUS_RUNNING, projectConfig.JOB_STATUS_NOT_START)
    cursor = db_connection.cursor()
    cursor.execute(sql, values)
    jobid = cursor.lastrowid
    return jobid


def endListSpriderJobStatus(db_connect_dict, job_id, status_list):
    host = db_connect_dict.get('MYSQL_HOST')
    database = db_connect_dict.get('MYSQL_DATABASE')
    user = db_connect_dict.get('MYSQL_USER')
    password = db_connect_dict.get('MYSQL_PASSWORD')
    port = db_connect_dict.get('MYSQL_PORT')
    if not host or not database or not user or not password or not port:
        raise ValueError('db connection dict missing in endListSpriderJobStatus')
    if not job_id:
        raise ValueError('job_id is empty in endListSpriderJobStatus')
    if not status_list:
        status_list = projectConfig.JOB_STATUS_FINISHED

    connection = mysql.connector.connect(host=host, database=database,
                                         user=user, password=password, port=port)
    cursor = connection.cursor()
    sql_item_count = 'select count(*) from kh_spider_job_items where job_id = %s'
    param1 = (job_id,)
    cursor.execute(sql_item_count, param1)
    total_number_list = 0
    result1 = cursor.fetchone()
    if result1 is not None:
        (total_number_list,) = result1

    sql = 'update kh_spider_job set status_list=%s, total_number_list=%s, end_time_list=now() where job_id=%s'
    values = (status_list, total_number_list, job_id)
    cursor.execute(sql, values)

    connection.commit()
    cursor.close()
    connection.close()


def deleteOldSpiderSourceItemByJobId(db_connection, site_url, resource_type, jobid, source_sitetag):
    sql = 'delete from kh_spider_job_items where site_url = %s and resource_type = %s and job_id < %s'
    values = (site_url, resource_type, jobid)
    if source_sitetag:
        sql += ' and source_sitetag = %s'
        values = (site_url, resource_type, jobid, source_sitetag)
    cursor = db_connection.cursor()
    cursor.execute(sql, values)


def startNewSpiderListJob(db_connect_dict, site_url, resource_type, source_sitetag):
    """begin new spider list job, 1. insert a new jobid,
    2. delete old scrapy data in table: kh_spider_job_items"""
    host = db_connect_dict.get('MYSQL_HOST')
    database = db_connect_dict.get('MYSQL_DATABASE')
    user = db_connect_dict.get('MYSQL_USER')
    password = db_connect_dict.get('MYSQL_PASSWORD')
    port = db_connect_dict.get('MYSQL_PORT')
    if not host or not database or not user or not password or not port:
        raise ValueError('db connection dict missing in startNewSpiderListJob')

    connection = mysql.connector.connect(host=host, database=database,
                                         user=user, password=password, port=port)
    # start new list spider job, so firstly insert into a new list job
    jobid = insertNewSpiderJob(connection, site_url, resource_type, source_sitetag)
    deleteOldSpiderSourceItemByJobId(connection, site_url, resource_type, jobid, source_sitetag)
    connection.commit()
    connection.close()

    return jobid


# insert into table: kh_medicine_article and kh_medicine_article_detail
# deprecated, see: addOneArticleMedicineOrDisease
"""
def addOneMedicineArticle(medicineArticleItem, db_connection):
    #insert table kh_medicine
    if not medicineArticleItem or not isinstance(medicineArticleItem, MedicineItem):
        raise ValueError('item is empty or is not a MedicineItem class, please check code')

    cursor = db_connection.cursor()
    if medicineArticleItem.IsResponseSuccess():
        medicineId = insertMedicineIfNotExist(medicineArticleItem, db_connection)
        # insert into kh_medicine_article
        insertTemplate = 'insert into kh_medicine_article (name, name_general, name_brand, medicine_id, language, ' \
                         'source_url, site_url, source_sitetag, spider_job_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        values = (medicineArticleItem.get("name"), medicineArticleItem.get("name_general"),
                  medicineArticleItem.get("name_brand"), medicineId, medicineArticleItem.get("language"),
                  medicineArticleItem.get("source_url"), medicineArticleItem.get("site_url"),
                  medicineArticleItem.get("source_sitetag"), medicineArticleItem.get("job_id"))
        cursor.execute(insertTemplate, values)
        articleId = cursor.lastrowid

        # insert into kh_medicine_article_detail
        insertTemplate_2 = 'insert into kh_medicine_article_detail (article_id, full_article) values (%s, %s)'
        values_2 = (articleId, medicineArticleItem.get("full_article"))
        cursor.execute(insertTemplate_2, values_2)

    # update job item status
    jobItemStatus = projectConfig.JOB_ITEM_STATUS_SUCCESS
    spider_log = ''
    if not medicineArticleItem.IsResponseSuccess():
        jobItemStatus = projectConfig.JOB_ITEM_STATUS_FAIL
        spider_log = 'error request, response_status:'+medicineArticleItem.get("response_status")\
                     + ', please check the log file for the detail'
    updateSpiderJobItemsStatus(cursor, None, medicineArticleItem.get("job_id"),
                               medicineArticleItem.get("source_url"), jobItemStatus, spider_log)

    db_connection.commit()
    cursor.close()
"""

# insert medicine name into table: kh_medicine if the medicine name is not exists
def insertMedicineIfNotExist(medicineArticleItem, db_connection):
    name = medicineArticleItem.get("name")
    if not name:
        print('error: name is empty in insertMedicineIfNotExist, source_url:'+medicineArticleItem.get("source_url"))
        return

    language = medicineArticleItem.get("language", 'en')
    name_english = name_chinese = None
    name_query = ''
    if language == 'en':
        name_english = name
        name_query = 'name_english = %s'
    elif language == 'zh':
        name_chinese = name
        name_query = 'name_chinese = %s'

    cursor = db_connection.cursor()

    # first check whether this medicine name exists in the table
    selectTemplate = 'select medicine_id from kh_medicine where '+name_query
    cursor.execute(selectTemplate, [name])
    result1 = cursor.fetchone()
    medicineId = ''
    if result1 is not None:
        (medicineId,) = result1

    if not medicineId:
        insertTemplate = 'insert into kh_medicine (name_english,name_chinese,name_general_temp, ' \
                         'is_general, source_url,spider_job_id) values (%s, %s, %s, %s, %s,%s)'

        values = (name_english, name_chinese, medicineArticleItem.get("name_general"),
                  medicineArticleItem.get("is_general"), medicineArticleItem.get("source_url"),
                  medicineArticleItem.get("job_id"))

        cursor.execute(insertTemplate, values)
        medicineId = cursor.lastrowid
        db_connection.commit()

    cursor.close()
    return medicineId

def getJobIdForDetailSpider(db_connection, resource_type):
    cursor = db_connection.cursor()
    sql = 'select max(job_id) from kh_spider_job where status_list=%s and status_detail=%s'
    params = (projectConfig.JOB_STATUS_FINISHED, projectConfig.JOB_STATUS_NOT_START)
    if resource_type:
        sql = sql+' and resource_type = %s'
        params = (projectConfig.JOB_STATUS_FINISHED, projectConfig.JOB_STATUS_NOT_START,
                  resource_type)

    cursor.execute(sql, params)
    (jobId,) = cursor.fetchone()
    cursor.close()
    return jobId


def getDBConnectionFromDict(db_connect_dict):
    host = db_connect_dict.get('MYSQL_HOST')
    database = db_connect_dict.get('MYSQL_DATABASE')
    user = db_connect_dict.get('MYSQL_USER')
    password = db_connect_dict.get('MYSQL_PASSWORD')
    port = db_connect_dict.get('MYSQL_PORT')
    if not host or not database or not user or not password or not port:
        raise ValueError('db connection dict missing in getSourceListForDetailJob')

    connection = mysql.connector.connect(host=host, database=database,
                                         user=user, password=password, port=port)
    return connection


BATCH_SELECT_SIZE = 1000

# get detail job items for spider
# only should fetch 1000 records each time，needs call this method more times until no record return
# caller can call this method more times until no records returns
def getSourceListForDetailJob(db_connection, job_id, resource_type, source_sitetag_list):
    if not db_connection:
        raise ValueError('db_connection is null in getSourceListForDetailJob')

    sourceSiteTagStr = ''
    if source_sitetag_list:
        sql_string = '(' + ','.join(["'%s'"] * len([x for x in source_sitetag_list if x])) + ')'
        sourceSiteTagStr = ' and source_sitetag in' + (sql_string % tuple([x for x in source_sitetag_list if x]))

    if not job_id or job_id < 1:
        job_id = getJobIdForDetailSpider(db_connection, resource_type)

    # preparing a cursor object
    # for testing, can add this: id in(34797,34798,34799)
    cursor = db_connection.cursor()
    query = "SELECT resource_type,name,source_url,site_url,source_sitetag,language,job_id FROM kh_spider_job_items " \
            "where resource_type=%s and status=%s and job_id=%s "+sourceSiteTagStr+" limit "+str(BATCH_SELECT_SIZE)
    params = (resource_type, projectConfig.JOB_ITEM_STATUS_NOT_START, job_id)
    cursor.execute(query, params)

    myresultList = cursor.fetchall()
    returnList = []
    for result in myresultList:
        item = {}
        item['resource_type'] = result[0]
        item['name'] = result[1]
        item['source_url'] = result[2]
        item['site_url'] = result[3]
        item['source_sitetag'] = result[4]
        item['language'] = result[5]
        item['job_id'] = result[6]
        returnList.append(item)

    # disconnecting from server
    cursor.close()
    return returnList


def updateSpiderJobItemsStatus(db_cursor, db_connection, job_id, source_url, status, spider_log):
    if not job_id or not source_url or not status:
        print('error: job_id or source_url or status is null: '+job_id+','+source_url+','+status)
        return
    timeUpdateStr = ''
    if status == projectConfig.JOB_ITEM_STATUS_RUNNING:
        timeUpdateStr = ' spider_time=now(),'
    else:
        timeUpdateStr = ' spider_end_time=now(),'
    sql = 'update kh_spider_job_items set status=%s,'+timeUpdateStr+' update_time=now(), spider_log=%s where job_id=%s and source_url=%s'
    values = (status, spider_log, job_id, source_url)

    needClose = False
    if not db_cursor:
        db_cursor = db_connection.cursor()
        needClose = True

    db_cursor.execute(sql, values)

    if needClose:
        db_connection.commit()
        db_cursor.close()


def updateStartJobDetailStatus(db_connect_dict, job_id):
    host = db_connect_dict.get('MYSQL_HOST')
    database = db_connect_dict.get('MYSQL_DATABASE')
    user = db_connect_dict.get('MYSQL_USER')
    password = db_connect_dict.get('MYSQL_PASSWORD')
    port = db_connect_dict.get('MYSQL_PORT')
    if not host or not database or not user or not password or not port:
        raise ValueError('db connection dict missing in getSourceListForDetailJob')

    sql = 'update kh_spider_job set status_detail=%s, start_time_detail=now() where job_id=%s'
    values = (projectConfig.JOB_STATUS_RUNNING, job_id)

    connection = mysql.connector.connect(host=host, database=database,
                                         user=user, password=password, port=port)
    cursor = connection.cursor()
    cursor.execute(sql, values)

    connection.commit()
    cursor.close()
    connection.close()


def endDetailSpiderJobStatus(db_connect_dict, job_id):
    connection = getDBConnectionFromDict(db_connect_dict)
    cursor = connection.cursor()

    sql_item_count = 'select count(*) from kh_spider_job_items where job_id = %s and status=%s'
    param1 = (job_id, projectConfig.JOB_ITEM_STATUS_SUCCESS)
    cursor.execute(sql_item_count, param1)
    success_number_list = 0
    result1 = cursor.fetchone()
    if result1 is not None:
        (success_number_list,) = result1

    # if successful job detail number equals total_number_list, means all records success, status_detail=3
    # else means all some record failed, status_detail=4
    update_sql = 'UPDATE kh_spider_job SET end_time_detail=now(), total_detail_finished=%s, ' \
                 'status_detail = CASE WHEN total_number_list = %s THEN 3 ELSE 4 END WHERE job_id = %s'
    param2 = (success_number_list, success_number_list, job_id)

    cursor = connection.cursor()
    cursor.execute(update_sql, param2)

    connection.commit()
    cursor.close()
    connection.close()


# insert into table: kh_medicine_article and kh_medicine_article_detail
def addOneArticleMedicineOrDisease(resource_type, item, db_connection):
    """insert table kh_medicine"""
    if not resource_type or not item:
        raise ValueError('resource_type is empty or item is empty')
    if resource_type == projectConfig.RESOURCE_TYPE_MEDICINE:
        if not isinstance(item, MedicineItem):
            raise ValueError('item is not a MedicineItem class, please check code')
    elif resource_type == projectConfig.RESOURCE_TYPE_DISEASE:
        if not isinstance(item, DiseaseItem):
            raise ValueError('item is not a DiseaseItem class, please check code')
    else:
        raise ValueError('please check resource_type, it should be either RESOURCE_TYPE_MEDICINE or RESOURCE_TYPE_DISEASE')

    cursor = db_connection.cursor()
    if item.IsResponseSuccess():
        if resource_type == projectConfig.RESOURCE_TYPE_MEDICINE:
            # insert medicine table first, then insert detail article table
            pkId = insertMedicineIfNotExist(item, db_connection)
            insertArticleMedicine(cursor, item, pkId)
        elif resource_type == projectConfig.RESOURCE_TYPE_DISEASE:
            # insert disease table first, then insert detail article table
            pkId = insertDiseaseIfNotExist(item, db_connection)
            insertArticleDisease(cursor, item, pkId)

    # update job item status
    jobItemStatus = projectConfig.JOB_ITEM_STATUS_SUCCESS
    spider_log = ''
    if not item.IsResponseSuccess():
        jobItemStatus = projectConfig.JOB_ITEM_STATUS_FAIL
        spider_log = 'error request, response_status:'+item.get("response_status")\
                     + ', please check the log file for the detail'
    updateSpiderJobItemsStatus(cursor, None, item.get("job_id"),
                               item.get("source_url"), jobItemStatus, spider_log)

    db_connection.commit()
    cursor.close()


# insert medicine name into table: kh_medicine if the medicine name is not exists
def insertDiseaseIfNotExist(articleItem, db_connection):
    name = articleItem.get("name")
    if not name:
        print('error: name is empty in insertDiseaseIfNotExist, source_url:'+articleItem.get("source_url"))
        return

    language = articleItem.get("language", 'en')
    name_english = name_chinese = None
    name_query = ''
    if language == 'en':
        name_english = name
        name_query = 'name_english = %s'
    elif language == 'zh':
        name_chinese = name
        name_query = 'name_chinese = %s'

    cursor = db_connection.cursor()

    # first check whether this disease name exists in the table
    selectTemplate = 'select disease_id from kh_disease where '+name_query
    cursor.execute(selectTemplate, [name])
    result1 = cursor.fetchone()
    pkId = ''
    if result1 is not None:
        (pkId,) = result1

    if not pkId:
        insertTemplate = 'insert into kh_disease (name_english,name_chinese, ' \
                         'source_url,spider_job_id) values (%s, %s, %s, %s)'

        values = (name_english, name_chinese,
                  articleItem.get("source_url"), articleItem.get("job_id"))

        cursor.execute(insertTemplate, values)
        pkId = cursor.lastrowid
        db_connection.commit()

    cursor.close()
    return pkId


def insertArticleMedicine(cursor, item, pkId):
    # insert into kh_medicine_article
    insertTemplate = 'insert into kh_medicine_article (name, name_general, name_brand, medicine_id, language, ' \
                     'source_url, site_url, source_sitetag, spider_job_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
    values = (item.get("name"), item.get("name_general"),
              item.get("name_brand"), pkId, item.get("language"),
              item.get("source_url"), item.get("site_url"),
              item.get("source_sitetag"), item.get("job_id"))
    cursor.execute(insertTemplate, values)
    articleId = cursor.lastrowid

    # insert into kh_medicine_article_detail
    insertTemplate_2 = 'insert into kh_medicine_article_detail (article_id, full_article) values (%s, %s)'
    values_2 = (articleId, item.get("full_article"))
    cursor.execute(insertTemplate_2, values_2)


def insertArticleDisease(cursor, item, pkId):
    # insert into kh_disease_article
    insertTemplate = 'insert into kh_disease_article (name, disease_id, language, source_url, ' \
                     'site_url, source_sitetag, spider_job_id) values (%s, %s, %s, %s, %s, %s, %s)'
    values = (item.get("name"), pkId, item.get("language"),
              item.get("source_url"), item.get("site_url"),
              item.get("source_sitetag"), item.get("job_id"))
    cursor.execute(insertTemplate, values)
    articleId = cursor.lastrowid

    # insert into kh_disease_article_detail
    insertTemplate_2 = 'insert into kh_disease_article_detail (article_id, full_article) values (%s, %s)'
    values_2 = (articleId, item.get("full_article"))
    # not commit, let its parent method to commit
    cursor.execute(insertTemplate_2, values_2)

