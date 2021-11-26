import configparser
from urllib.parse import urlparse

import pandas as pd
import urllib.request
from crawling import config
import requests
import sqlalchemy
from sqlalchemy import create_engine

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def request_naver(source, query, start):
    client_id = config['CRAWLING_CONFIG']['Naver_API_ID']
    client_secret = config['CRAWLING_CONFIG']['Naver_API_SECRET']
    header = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}
    encText = urllib.parse.quote(query)

    if source == 'blog':
        url = "https://openapi.naver.com/v1/search/blog.json?query=" + encText + "&display=100&start=" + str(start) # json 결과
    elif source == 'cafe':
        url = "https://openapi.naver.com/v1/search/cafearticle.json?query=" + encText + "&display=100&start=" + str(start) # json 결과

    r = requests.get(urlparse(url).geturl(), headers=header)
    if r.status_code == 200:
        return r.json()
    
    else:
        print(r)
        return r.status_code

def get_naver(source, query):
    list = []
    page = 0
    if source == 'blog':
        while page < 10:  # 검색 시작 위치로 최대 1000까지 가능
            json_obj = (request_naver(source, query, (page * 100) + 1))  # 한 페이지 당 최대 100개 가능
            for document in json_obj['items']:
                val = [document['title'].replace("<b>", "").replace("</b>", "").replace("amp;", ""),
                       document['description'].replace("<b>", "").replace("</b>", ""),
                       document['bloggername'], document['postdate'], document['link']]
                list.append(val)
            page += 1
            if json_obj['total'] < (page * 100): break
    elif source == 'cafe':
        while page < 10:  # 검색 시작 위치로 최대 1000까지 가능
            json_obj = (request_naver(source, query, (page * 100) + 1))  # 한 페이지 당 최대 100개 가능
            for document in json_obj['items']:
                val = [document['title'].replace("<b>", "").replace("</b>", "").replace("amp;", ""),
                       document['description'].replace("<b>", "").replace("</b>", ""),
                       document['cafename'], document['link']]
                list.append(val)
            page += 1
            if json_obj['total'] < (page * 100): break
    return list

def url_naver(query):
    db_connection_str = config['MYSQL_CONFIG']['db_connection']
    db_connection = create_engine(db_connection_str)

    json_list_blog = get_naver('blog', query)
    source = 'naver_blog'

    for i, list in enumerate(json_list_blog):
        try:
            sql = "CREATE TABLE naver_openApi (  id INT NOT NULL AUTO_INCREMENT,  title VARCHAR(100) NULL, content TEXT NULL,  name VARCHAR(100) NULL, postdate DATETIME NULL, url VARCHAR(500) NULL, query VARCHAR(45) NULL,  source VARCHAR(45) NULL, PRIMARY KEY (id), UNIQUE INDEX  url_UNIQUE (url ASC)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci;"
            db_connection.execute(sql)
            print('create table')
        except:
            print('', end='')

        sql = "SELECT count(*) FROM naver_openApi WHERE url = %s"
        result = db_connection.execute(sql, (list[4]))
        result = (result.first()[0])
        if result > 0:
            print(i, ': ', list[4], ' skip')
        else:
            sql = "INSERT INTO naver_openApi (title, content, name, postdate, url, query, source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            db_connection.execute(sql, (list[0], list[1], list[2], list[3], list[4], query, source))
            print(i, ': ', list[4], ' done')


    # json_list_cafe = get_naver('cafe', query)
    #
    # source = 'naver_cafe'
    #
    # for i, list in enumerate(json_list_cafe):
    #     try:
    #         sql = "CREATE TABLE `crawling`.`naver_openApi` (  `id` INT NOT NULL AUTO_INCREMENT,  `title` VARCHAR(100) NULL, `content` TEXT NULL,  `name` VARCHAR(100) NULL, `postdate` DATETIME NULL, `url` VARCHAR(100) NULL, `query` VARCHAR(45) NULL,  `source` VARCHAR(45) NULL, PRIMARY KEY (`id`), UNIQUE INDEX `url_UNIQUE` (`url` ASC) VISIBLE);"
    #         db_connection.execute(sql)
    #         print('create table')
    #     except:
    #         print(end='')
    #
    #     sql = "SELECT count(*) FROM naver_openApi WHERE url = %s"
    #     result = db_connection.execute(sql, (list[4]))
    #     result = (result.first()[0])
    #     if result > 0:
    #         print(i, ': ', list[4], ' skip')
    #     else:
    #         sql = "INSERT INTO naver_openApi (title, content, name, postdate, url, query, source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    #         db_connection.execute(sql, (list[0], list[1], list[2], list[3], list[4], query, source))
    #         print(i, ': ', list[4], ' done')
    #
    # df_c = pd.DataFrame(json_list_cafe, columns=['title', 'contents', 'name', 'url'])
    # df_c['query'] = query
    # df_c['source'] = '네이버카페'
    # df_c.to_excel('Crawler/Crawling_Result/URL_DATA/' + query + '_Naver_cafe' + '.xlsx', index=True, index_label = "id")