from scrapy.http import Request
from diseasebot import projectConfig
from diseasebot import settings
from diseasebot import dbBizUtils
import datetime,time

WEB_SITE_DRUGS = 'https://www.drugs.com'


alphabets = list('abcdefghijklmnopqrstuvwxyz')
alphabets.append('0-9')


# see config_demo_sample.json, node: start_urls
# def medicine_list_drugs_start_url():
#     # tag is: a2z
#     for x in alphabets:
#         yield 'https://www.drugs.com/alpha/'+x+'.html'
#     # tag is: fda
#     for x in alphabets:
#         yield 'https://www.drugs.com/alpha/'+x+'.html?pro=1'

def medicine_list_drugs_start_requests():
    # tag is: a2z
    for x in alphabets:
        yield Request(url='https://www.drugs.com/alpha/'+x+'.html',
                      meta={projectConfig.REQUEST_META_PREFIX+"source_sitetag": projectConfig.SOURCE_SITETAG_A2Z},
                      dont_filter=True)

    # tag is: fda
    for x in alphabets:
        yield Request(url='https://www.drugs.com/alpha/' + x + '.html?pro=1',
                      meta={projectConfig.REQUEST_META_PREFIX+"source_sitetag": projectConfig.SOURCE_SITETAG_FDA},
                      dont_filter=True)


def getMysqlParametersFromFile():
     return {'MYSQL_HOST': settings.MYSQL_HOST, 'MYSQL_DATABASE': settings.MYSQL_DATABASE,
             'MYSQL_USER': settings.MYSQL_USER, 'MYSQL_PASSWORD': settings.MYSQL_PASSWORD,
             'MYSQL_PORT': settings.MYSQL_PORT}


# def get_medicine_detail_start_url(source_sitetags=''):
#     return get_detail_resource_start_url(source_sitetags)
#
#
# def get_disease_detail_start_url(source_sitetags=''):
#     return get_detail_resource_start_url(source_sitetags)


# get each article spider url for spider
def get_detail_resource_start_url(source_sitetag_str):
    if projectConfig.JobId < 0:
        raise ValueError('missing JobId in get_detail_resource_start_url, job_id:'+projectConfig.JobId)
    taglist = []
    if source_sitetag_str and ',' in str(source_sitetag_str):
        taglist = [x.strip() for x in str(source_sitetag_str).split(',') if x.strip()]
    elif source_sitetag_str:
        taglist.append(str(source_sitetag_str).strip())

    resource_type = projectConfig.getResourceType()
    db_connect_dict = getMysqlParametersFromFile()
    # if the search size is equal 5000, then do another search,
    # because when finished an item spider, the status will be changed
    db_connection = dbBizUtils.getDBConnectionFromDict(db_connect_dict)
    loop_flag = True
    processBegin_number = 0
    sendRequest_number = 0
    while loop_flag:
        returnList = dbBizUtils.getSourceListForDetailJob(db_connection, projectConfig.JobId, resource_type, taglist)
        if returnList and len(returnList) > 0:
            print('---- progressing, begin %d to %d' % (processBegin_number, processBegin_number+len(returnList)))
            processBegin_number += len(returnList)

            for item in returnList:
                # update job item status to running
                dbBizUtils.updateSpiderJobItemsStatus(None, db_connection, projectConfig.JobId,
                                                      item['source_url'], projectConfig.JOB_ITEM_STATUS_RUNNING, '')
                sendRequest_number += 1
                print('---- begin request for: %s , time: %s' % (item['source_url'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                yield Request(url=item['source_url'],
                              meta={projectConfig.REQUEST_META_PREFIX+"name": item['name'],
                                    projectConfig.REQUEST_META_PREFIX+"source_url": item['source_url'],
                                    projectConfig.REQUEST_META_PREFIX+"site_url": item.get('site_url'),
                                    projectConfig.REQUEST_META_PREFIX+"source_sitetag": item.get('source_sitetag'),
                                    projectConfig.REQUEST_META_PREFIX+"language": item.get('language'),
                                    projectConfig.REQUEST_META_PREFIX+"job_id": item['job_id'],
                                    projectConfig.REQUEST_META_PREFIX+"resource_type": resource_type},
                              dont_filter=True)

            if len(returnList) < dbBizUtils.BATCH_SELECT_SIZE:
                loop_flag = False
        else:
            print('select result is None, job_id:'+str(projectConfig.JobId))

    db_connection.close()

