from diseasebot import dbBizUtils
from diseasebot import settings


def testMysqlConnection():
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
    cursor = db_connection.cursor()
    query = 'SELECT article_id,name,source_url,language FROM kh_disease_article limit 3'
    cursor.execute(query)

    myresultList = cursor.fetchall()
    item = {}
    item['article_id'] = str(myresultList[0][0])
    item['name'] = myresultList[0][1]
    item['source_url'] = myresultList[0][2]
    item['language'] = myresultList[0][3]

    db_connection.close()

    print('article_id:'+item['article_id']+', name:'+item['name']+', source_url:'+item['source_url'])


testMysqlConnection()

