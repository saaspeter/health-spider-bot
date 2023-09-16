from os.path import realpath, dirname
import json
import threading
from scrapy.utils.project import get_project_settings


custom_setting = None
scrapy_setting = None

# for get medicine page, and get each medicine list
TASK_TYPE_SPIDER_MEDICINE_LIST = 'spider_medicine_list'
# get each medicine detail task
TASK_TYPE_SPIDER_MEDICINE_DETAILS = 'spider_medicine_details'

# for get medicine page, and get each medicine list
TASK_TYPE_SPIDER_DISEASE_LIST = 'spider_disease_list'
# get each medicine detail task
TASK_TYPE_SPIDER_DISEASE_DETAIL = 'spider_disease_detail'

RESOURCE_TYPE_MEDICINE = 1
RESOURCE_TYPE_DISEASE = 2

SOURCE_SITETAG_A2Z = 'common_A2Z'
SOURCE_SITETAG_FDA = 'FDA'
SOURCE_SITETAG_MAYOCLINIC = 'MayoClinic'
SOURCE_SITETAG_HARVARDHEALTH = 'HarvardHealth'

# all customized meta key must start with it,
# because this method: copyMetaToNewRequest only copy meta keys with below prefix
# to it sub new request in rules
REQUEST_META_PREFIX = '_custom_'

# kh_spider_job status
JOB_STATUS_NOT_START = 1
JOB_STATUS_RUNNING = 2
JOB_STATUS_FINISHED = 3

# kh_spider_job_items status
JOB_ITEM_STATUS_NOT_START = 1
JOB_ITEM_STATUS_RUNNING = 2
JOB_ITEM_STATUS_SUCCESS = 3
JOB_ITEM_STATUS_FAIL = 4

JobId = -1


def getResourceType():
    task_type = getTaskType()
    if task_type == TASK_TYPE_SPIDER_MEDICINE_LIST or task_type == TASK_TYPE_SPIDER_MEDICINE_DETAILS:
        return RESOURCE_TYPE_MEDICINE
    elif task_type == TASK_TYPE_SPIDER_DISEASE_LIST or task_type == TASK_TYPE_SPIDER_DISEASE_DETAIL:
        return RESOURCE_TYPE_DISEASE
    else:
        raise ValueError('unsupported task_type:' + task_type)


def isTaskListJob():
    task_type = getTaskType()
    if task_type == TASK_TYPE_SPIDER_MEDICINE_LIST or task_type == TASK_TYPE_SPIDER_DISEASE_LIST:
        return 1
    else:
        return 0

def isTaskArticleDetailJob():
    task_type = getTaskType()
    if task_type == TASK_TYPE_SPIDER_MEDICINE_DETAILS or task_type == TASK_TYPE_SPIDER_DISEASE_DETAIL:
        return 1
    else:
        return 0

def load_config(name):
    global custom_setting
    custom_setting = None
    # load custom config files
    path = dirname(realpath(__file__)) + '/configs/' + name + '.json'
    with open(path, 'r', encoding='utf-8') as f:
        custom_setting = json.loads(f.read())
        return custom_setting


def getFromConfigFileSetting(key):
    if custom_setting:
        return custom_setting.get(key)
    else:
        return ''

def getLanguageSite():
    if custom_setting:
        return custom_setting.get("language")
    else:
        return ''

def getWebSite():
    if custom_setting:
        val = custom_setting.get("website")
        if val:
            if str(val).endswith('/'):
                return str(val)[:-1]
            else:
                return val
        else:
            raise ValueError('website not set, format is like: https://drugs.com')
    else:
        raise ValueError('not set custom setting json')


def getTaskType():
    if custom_setting:
        val = custom_setting.get("task_type")
        if val:
            return val
        else:
            raise ValueError('task_type not set')
    else:
        raise ValueError('not set custom setting json')


def getSourceSitetags_global():
    if custom_setting:
        sourceSiteTagNode = custom_setting.get('item').get('attrs').get('source_sitetag')
        if sourceSiteTagNode and sourceSiteTagNode[0].get('method') == 'value':
            tags = sourceSiteTagNode[0].get('args')[0]
            return tags
    return None


def isSupportedTaskType(task_type):
    if task_type == TASK_TYPE_SPIDER_MEDICINE_LIST or task_type == TASK_TYPE_SPIDER_MEDICINE_DETAILS\
            or task_type == TASK_TYPE_SPIDER_DISEASE_LIST or task_type == TASK_TYPE_SPIDER_DISEASE_DETAIL:
        return True
    else:
        return False

def getFromScrapySetting(key):
    if scrapy_setting:
        return scrapy_setting.get(key)
    else:
        raise ValueError('can not read scrapy setting')


def getDBConnectDict():
    host = getFromScrapySetting('MYSQL_HOST')
    database = getFromScrapySetting('MYSQL_DATABASE')
    user = getFromScrapySetting('MYSQL_USER')
    password = getFromScrapySetting('MYSQL_PASSWORD')
    port = getFromScrapySetting('MYSQL_PORT')

    return {'MYSQL_HOST': host, 'MYSQL_DATABASE': database,
            'MYSQL_USER': user, 'MYSQL_PASSWORD': password, 'MYSQL_PORT': port}

