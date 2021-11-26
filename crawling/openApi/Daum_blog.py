import configparser

import requests
import json
import pandas as pd
from urllib.parse import urlparse
from crawling import config
from sqlalchemy import create_engine

############ 카카오 검색 API를 이용한 '깃대종' 블로그/카페 검색 가시화  https://blog.daum.net/geoscience/1412

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def request_daum(source, query, page):
    if source == 'blog':
        url = "https://dapi.kakao.com/v2/search/blog?&query="+query+"&size=50"+"&page="+str(page)
    elif source == 'cafe':
        url = "https://dapi.kakao.com/v2/search/cafe?&query="+query+"&size=50"+"&page="+str(page)
    else:
        return False
    header = {'authorization':'KakaoAK '+config['CRAWLING_CONFIG']['Daum_REST_API_KEY']}    # 그럼 뭘로 하라는겨

    r = requests.get(urlparse(url).geturl(), headers=header)
    if r.status_code == 200:
        return r.json()
    else:
        return r.error

def get_daum(source, query):
    list=[]
    page = 1
    if source == 'blog':
        while page <= 50:
            json_obj = request_daum(source, query, page)
            for document in json_obj['documents']:
                val = [document['title'].replace("<b>", "").replace("</b>", ""),
                       document['contents'],
                       document['blogname'], document['datetime'][:10], document['url']]
                list.append(val)
            if json_obj['meta']['is_end'] is True: break
            page += 1
    elif source == 'cafe':
        while page <= 50:
            json_obj = request_daum(source, query, page)
            for document in json_obj['documents']:
                val = [document['title'].replace("<b>", "").replace("</b>", ""),
                       document['contents'],
                       document['cafename'].replace("&lt;","").replace("&gt;",""), document['datetime'][:10], document['url']]
                list.append(val)
            if json_obj['meta']['is_end'] is True: break
            page += 1
    return list


def url_daum(query):
    db_connection = create_engine(config['MYSQL_CONFIG']['db_connection'])

    json_list_blog = get_daum('blog', query)

    for i, list in enumerate(json_list_blog):
        try:
            sql = "CREATE TABLE daum_openApi (  id INT NOT NULL AUTO_INCREMENT,  title VARCHAR(100) NULL, content TEXT NULL,  name TEXT NULL, postdate DATETIME NULL, url VARCHAR(500) NULL, query VARCHAR(45) NULL,  source VARCHAR(45) NULL, PRIMARY KEY (id), UNIQUE INDEX url_UNIQUE (url ASC)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci;"
            db_connection.execute(sql)
            print('create table')
        except:
            print(end='')

        sql = "SELECT count(*) FROM naver_openApi WHERE url = %s"
        naver_ = db_connection.execute(sql, (list[4]))
        result = (naver_.first()[0])

        sql = "SELECT count(*) FROM daum_openApi WHERE url = %s"
        daum_ = db_connection.execute(sql, (list[4]))
        result += (daum_.first()[0])

        if result > 0:
            print(i, ': ', list[4], ' skip')
        else:
            if 'naver' in list[4]:
                source = 'naver_blog'
                sql = "INSERT INTO naver_openApi (title, content, name, postdate, url, query, source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source)
            else :
                source = 'daum_blog'
                sql = "INSERT INTO daum_openApi (title, content, name, postdate, url, query, source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source)
            print(i, ': ', list[4], ' done')

    json_list_cafe = get_daum('cafe', query)

    for i, list in enumerate(json_list_cafe):
        try:
            sql = "CREATE TABLE daum_openApi (  id INT NOT NULL AUTO_INCREMENT,  title VARCHAR(100) NULL, content TEXT NULL,  name TEXT NULL, postdate DATETIME NULL, url VARCHAR(500) NULL, query VARCHAR(45) NULL,  source VARCHAR(45) NULL, PRIMARY KEY (id), UNIQUE INDEX url_UNIQUE (url ASC)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci;"
            db_connection.execute(sql)
            print('create table')
        except:
            print(end='')

        sql = "SELECT count(*) FROM naver_openApi WHERE url = %s"
        naver_ = db_connection.execute(sql, (list[4]))
        result = (naver_.first()[0])

        sql = "SELECT count(*) FROM daum_openApi WHERE url = %s"
        daum_ = db_connection.execute(sql, (list[4]))
        result += (daum_.first()[0])

        if result > 0:
            print(i, ': ', list[4], ' skip')
        else:
            if 'naver' in list[4]:
                source = 'naver_cafe'
                sql = "INSERT INTO naver_openApi (title, content, name, postdate, url, query, source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source)
            else :
                source = 'daum_cafe'
                sql = "INSERT INTO daum_openApi (title, content, name, postdate, url, query, source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source)
            print(i, ': ', list[4], ' done')
