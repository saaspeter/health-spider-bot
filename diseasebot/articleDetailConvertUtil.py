from diseasebot import dbBizUtils, utils
from diseasebot import projectConfig
from diseasebot import settings


def _getDBConnection():
    host = settings.MYSQL_HOST
    port = settings.MYSQL_PORT
    database = settings.MYSQL_DATABASE
    user = settings.MYSQL_USER
    password = settings.MYSQL_PASSWORD
    connection_dict = {'MYSQL_HOST': host,
                       'MYSQL_PORT': port,
                       'MYSQL_DATABASE': database,
                       'MYSQL_USER': user,
                       'MYSQL_PASSWORD': password
                       }
    db_connection = dbBizUtils.getDBConnectionFromDict(connection_dict)
    return db_connection

def insertArticleDetailFromHtmlToText(resource_type):
    detail_table_name = 'kh_disease_article_detail'
    detail_text_table_name = 'kh_disease_article_detail_text'
    if resource_type == projectConfig.RESOURCE_TYPE_MEDICINE:
        detail_table_name = 'kh_medicine_article_detail'
        detail_text_table_name = 'kh_medicine_article_detail_text'

    batch_size = 10
    offset = 0
    db_connection = _getDBConnection()
    cursor = db_connection.cursor()

    query = 'SELECT article_id,full_article FROM '+detail_table_name+' limit %s, '+str(batch_size)
    #test_query = 'SELECT article_id,full_article FROM ' + detail_table_name + ' limit 3'
    insertTemplate = 'insert into ' + detail_text_table_name + ' (article_id, full_article) values (%s, %s)'
    loop = True

    while loop:
        print('-------- begin to process: {}, batch size:{}'.format(offset, batch_size))
        params = (offset,)
        cursor.execute(query, params)

        myresultList = cursor.fetchall()
        if myresultList and len(myresultList) > 0:
            returnList = []
            offset += len(myresultList)
            for result in myresultList:
                item = {}
                item['article_id'] = result[0]
                item['full_article'] = utils.extractTextFromHtml(result[1])
                #print('--clean text, id:{}'.format(item['article_id']))
                #print(item['full_article'])
                #print('\n\n')
                returnList.append(item)

            for item2 in returnList:
                params_2 = (item2['article_id'], item2.get("full_article"))
                cursor.execute(insertTemplate, params_2)

            db_connection.commit()
            if len(myresultList) < batch_size:
                loop = False

            print('-------- finished process to: {}'.format(offset))
        else:
            loop = False
        print('-------- end all data, total: {}'.format(offset))
    db_connection.close()


def printSampleInArticleDetail(resource_type):
    detail_text_table_name = 'kh_disease_article_detail_text'
    if resource_type == projectConfig.RESOURCE_TYPE_MEDICINE:
        detail_text_table_name = 'kh_medicine_article_detail_text'

    batch_size = 2
    db_connection = _getDBConnection()
    cursor = db_connection.cursor()

    query = 'SELECT article_id,full_article FROM ' + detail_text_table_name + ' limit ' + str(batch_size)
    cursor.execute(query)
    myresultList = cursor.fetchall()
    if myresultList and len(myresultList) > 0:
        for result in myresultList:
            print('--clean text, id:{}'.format(result[0]))
            print(result[1])
            print('\n\n')


# begin to run
insertArticleDetailFromHtmlToText(projectConfig.RESOURCE_TYPE_MEDICINE)

# print sample data
#printSampleInArticleDetail(projectConfig.RESOURCE_TYPE_DISEASE)

