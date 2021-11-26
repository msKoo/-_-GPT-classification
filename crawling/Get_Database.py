import configparser

import pymysql
from datetime import datetime, timedelta

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def get_blog_url(query):
    conn = pymysql.connect(
        host = config['MYSQL_CONFIG']['sql_host'],
        user = config['MYSQL_CONFIG']['user'],
        password = config['MYSQL_CONFIG']['password'],
        db = config['MYSQL_CONFIG']['db'],
        charset = config['MYSQL_CONFIG']['charset']
    )

    curs = conn.cursor()

    f = '%Y-%m-%d %H:%M:%S'

    sql = "select * from naver_openApi where query = %s"
    curs.execute(sql, query)

    rows = curs.fetchall()

    id = []
    title= []
    content = []
    postdate= []
    url = []
    source = []
    for row in rows:
        id.append(row[0])
        title.append(row[1])
        content.append(row[2])
        postdate.append(row[4].strftime(f))
        url.append(row[5])
        source.append(row[7])


    conn.close()

    print(url)

    return title, content, postdate, url, source

def get_youtube(query):
    conn = pymysql.connect(
        host=config['MYSQL_CONFIG']['sql_host'],
        user=config['MYSQL_CONFIG']['user'],
        password=config['MYSQL_CONFIG']['password'],
        db=config['MYSQL_CONFIG']['db'],
        charset=config['MYSQL_CONFIG']['charset']
    )

    curs = conn.cursor()

    sql = "select * from Crawl_youtube where query = %s"
    curs.execute(sql, query)

    rows = curs.fetchall()

    id = []
    content = []
    postdate= []
    url = []
    source = []
    for row in rows:
        id.append(row[0])
        content.append(row[2])
        postdate.append(row[4])
        url.append(row[1])
        source.append(row[6])

    conn.close()

    return id, content, postdate, url, source

def get_blog_content(query):
    conn = pymysql.connect(
        host = config['MYSQL_CONFIG']['sql_host'],
        user = config['MYSQL_CONFIG']['user'],
        password = config['MYSQL_CONFIG']['password'],
        db = config['MYSQL_CONFIG']['db'],
        charset = config['MYSQL_CONFIG']['charset']
    )

    curs = conn.cursor()

    sql = "select * from Crawl_blog where query = %s"
    curs.execute(sql, query)

    f = '%Y-%m-%d %H:%M:%S'

    rows = curs.fetchall()

    id = []
    title= []
    content = []
    postdate= []
    url = []
    source = []
    for row in rows:
        id.append(row[0])
        content.append(row[3])
        postdate.append(row[5])
        url.append(row[2])
        source.append(row[4])


    conn.close()

    return id, content, postdate, url, source

def get_today_blog(query,source, dura):
    # naver_blog,  daum_blog,   daum_cafe'
    conn = pymysql.connect(
        host=config['MYSQL_CONFIG']['sql_host'],
        user=config['MYSQL_CONFIG']['user'],
        password=config['MYSQL_CONFIG']['password'],
        db=config['MYSQL_CONFIG']['db'],
        charset=config['MYSQL_CONFIG']['charset']
    )
    result = []
    mon_len = 0
    curs = conn.cursor()

    if 'naver' in source:
        for i in range (0,dura):
            today = datetime.today() - timedelta(i)
            today = today.strftime("%Y-%m-%d")

            sql = "select * from naver_openApi where query = %s AND postdate = %s AND source=%s"
            curs.execute(sql, (query, today, source))
            rows = (curs.fetchall())
            mon_len += len(rows)
            result.append(rows)

    elif 'daum' in source:
        for i in range(0, dura):
            today = datetime.today() - timedelta(i)
            today = today.strftime("%Y-%m-%d")

            sql = "select * from daum_openApi where query = %s AND postdate = %s AND source=%s"
            curs.execute(sql, (query, today, source))
            rows = (curs.fetchall())
            mon_len += len(rows)
            result.append(rows)

    conn.close()
    return mon_len, result

def get_today_youtube(query, dura):
    conn = pymysql.connect(
        host=config['MYSQL_CONFIG']['sql_host'],
        user=config['MYSQL_CONFIG']['user'],
        password=config['MYSQL_CONFIG']['password'],
        db=config['MYSQL_CONFIG']['db'],
        charset=config['MYSQL_CONFIG']['charset']
    )
    result = []
    mon_len = 0
    curs = conn.cursor()

    for i in range (0,dura):
        today = datetime.today() - timedelta(i)
        today = today.strftime("%Y-%m-%d")

        sql = "select * from Crawl_youtube where query = %s AND postdate = %s"
        curs.execute(sql, (query, today))
        rows = (curs.fetchall())
        mon_len += len(rows)
        result.append(rows)

    conn.close()

    return mon_len, result

def get_recent_boardList(query, source, listNum):
    # query, source, 출력할 리스트 갯수 출력
    conn = pymysql.connect(
        host=config['MYSQL_CONFIG']['sql_host'],
        user=config['MYSQL_CONFIG']['user'],
        password=config['MYSQL_CONFIG']['password'],
        db=config['MYSQL_CONFIG']['db'],
        charset=config['MYSQL_CONFIG']['charset']
    )
    curs = conn.cursor()

    if source == 'naver_blog':
        # id title content name postdate url query source
        sql = "select * FROM naver_openApi WHERE query = %s AND source = %s ORDER BY postdate DESC LIMIT %s"
    elif source == 'daum_blog' or source == 'daum_cafe':
        # id title content name postdate url query source
        sql = "select * FROM daum_openApi WHERE query = %s AND source = %s ORDER BY postdate DESC LIMIT %s"
    elif 'youtube' in source:
        # id content author postdate url query source num_likes
        sql = "select * FROM youtube_openApi WHERE query = %s AND source = %s ORDER BY postdate DESC LIMIT %s"

    curs.execute(sql, (query, source, listNum))
    rows = curs.fetchall()

    for rpo in rows:
        print(rpo)
    conn.close()
    return rows


def get_detail_boardList(query, source, detail, listNum):
    # query, source, 출력할 리스트 갯수 출력
    conn = pymysql.connect(
        host=config['MYSQL_CONFIG']['sql_host'],
        user=config['MYSQL_CONFIG']['user'],
        password=config['MYSQL_CONFIG']['password'],
        db=config['MYSQL_CONFIG']['db'],
        charset=config['MYSQL_CONFIG']['charset']
    )
    curs = conn.cursor()

    if 'youtube' in source:
        # id content author postdate url query source num_likes
        sql = "select sent.*, api.title FROM sentimentAnal_youtube sent LEFT JOIN youtube_openApi api " \
              "ON sent.url = api.url WHERE sent.query = %s AND sent.source = %s AND sent.sentiAnal_detail = %s " \
              "ORDER BY sent.postdate DESC LIMIT %s"
        curs.execute(sql, (query, source, detail, listNum))
        rows = curs.fetchall()
    else:
        sql = "select * FROM sentiementAnal WHERE query = %s AND source = %s AND sentiAnal_detail = %s ORDER BY postdate DESC LIMIT %s"
        curs.execute(sql, (query, source, detail, listNum))
        rows = curs.fetchall()

    conn.close()
    return rows

def get_sentence_senti_detail(query, source, senti, num):
    conn = pymysql.connect(
        host=config['MYSQL_CONFIG']['sql_host'],
        user=config['MYSQL_CONFIG']['user'],
        password=config['MYSQL_CONFIG']['password'],
        db=config['MYSQL_CONFIG']['db'],
        charset=config['MYSQL_CONFIG']['charset']
    )
    curs = conn.cursor()

    result = []

    if 'youtube' in source:
        sql = "select * FROM sentimentAnal_youtube WHERE query = %s AND sentiAnal_detail=%s ORDER BY postdate DESC LIMIT %s"
        curs.execute(sql, (query, senti, num))
        result = curs.fetchall()
    else:
        sql = "select url FROM sentimentAnal WHERE query = %s AND sentiAnal_detail = %s ORDER BY postdate DESC LIMIT %s"
        curs.execute(sql, (query, senti, num))
        urls = curs.fetchall()
        if 'naver_blog' == source:
            sql = "select * FROM naver_openApi WHERE url = %s"
        elif 'daum_blog' == source or 'daum_cafe' == source:
            sql = "select * FROM daum_openApi WHERE url = %s"
        for url in urls:
            curs.execute(sql, url)
            result += (curs.fetchall())

    for re in result:
        print(re)
    conn.close()

    return result