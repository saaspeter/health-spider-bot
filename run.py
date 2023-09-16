import sys
from scrapy.utils.project import get_project_settings
import diseasebot.projectConfig as projectConfig
from scrapy.crawler import CrawlerProcess
from diseasebot import dbBizUtils
import time
import datetime


def run():
    name = sys.argv[1]
    if not name:
        raise ValueError("run parameter:name is empty!")
    else:
        print('------ Run parameters, name:'+name)

    start_time = time.time()
    print('---- begin Scrawl job, config file name: %s, time:%s' % (name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    custom_settings = projectConfig.load_config(name)
    # precheck config file setting
    preCheckConfigFileContent(custom_settings)

    spider = custom_settings.get('spider', 'universal')

    project_settings = get_project_settings()
    scrapy_settings = dict(project_settings.copy())
    scrapy_settings.update(custom_settings.get('settings'))
    projectConfig.scrapy_setting = scrapy_settings

    # pre-work before crawl
    preWorkBeforeCrawl()

    # begin scrapy
    process = CrawlerProcess(scrapy_settings)
    process.crawl(spider, **{'name': name})
    process.start()

    # post-work after crawl
    postWorkAfterCrawl()

    time_cost = time.time() - start_time
    print('---- finished Scrawl job, end time: %s, time cost: %.2f 秒, ' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), time_cost))


def preCheckConfigFileContent(custom_file_settings):
    if not custom_file_settings.get('spider'):
        raise ValueError("error: spider in json config file is empty!")
    if not custom_file_settings.get('website'):
        raise ValueError("error: website in json config file is empty!")
    if not projectConfig.isSupportedTaskType(custom_file_settings.get('task_type')):
        raise ValueError("error: task_type in json config file is empty or not supported task type!")
    if not custom_file_settings.get('settings'):
        raise ValueError("error: settings in json config file is empty!")
    if projectConfig.isTaskArticleDetailJob() and not custom_file_settings.get('job_id'):
        raise ValueError("error: the job_id in json config file is empty, must designate it for article detail job!")
    return


def preWorkBeforeCrawl():
    if projectConfig.isTaskListJob():
        jobId = dbBizUtils.startNewSpiderListJob(projectConfig.getDBConnectDict(),
                                                 projectConfig.getWebSite(),
                                                 projectConfig.getResourceType(),
                                                 projectConfig.getSourceSitetags_global())
        projectConfig.JobId = jobId
    else:
        # for detail work
        jobIdStr = projectConfig.getFromConfigFileSetting('job_id')
        if jobIdStr and str(jobIdStr).strip():
            projectConfig.JobId = int(str(jobIdStr).strip())
        dbBizUtils.updateStartJobDetailStatus(projectConfig.getDBConnectDict(),projectConfig.JobId)


def postWorkAfterCrawl():
    if projectConfig.isTaskListJob():
        dbBizUtils.endListSpriderJobStatus(projectConfig.getDBConnectDict(),
                                           projectConfig.JobId, projectConfig.JOB_STATUS_FINISHED)
    else:
        dbBizUtils.endDetailSpiderJobStatus(projectConfig.getDBConnectDict(), projectConfig.JobId)
        # update job status


if __name__ == '__main__':
    run()
