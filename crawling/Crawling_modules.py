import configparser
import time
import random

from crawling.crawler.Naver_BLOGandCAFE import naver
from crawling.crawler.Daum_BLOGandCAFE import daum
from crawling.openApi.YOUTUBE_comment import request_youtube, get_video_comments
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sqlalchemy import create_engine

def BLOG_Crawler(query):
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    options = Options()

    query = query
    options.add_argument(
        'user-agent=' + "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36")
    options.add_argument('headless')
    options.add_argument('--window-size= 360, 360')  # 실행되는 브라우저 크기를 지정할 수 있습니다.
    options.add_argument('--blink-settings=imagesEnabled=false')  # 브라우저에서 이미지 로딩을 하지 않습니다.

    path = '/home/drsong/download/chromedriver'    # linux server

    driver = webdriver.Chrome(executable_path=path,
                                   options=options)

    db_connection_str = 'mysql+pymysql://saso:saso@localhost/DAMDA'
    db_connection = create_engine(db_connection_str)
    sql = "SELECT postdate, url, title FROM  naver_openApi WHERE query = \'"+query+"\';"
    df = pd.read_sql(sql, db_connection)
    url_list = df['url'].values.tolist()

    for i, url in enumerate(url_list):
        try:
            sql = "CREATE TABLE Crawl_blog (  id INT NOT NULL AUTO_INCREMENT,  query VARCHAR(45) NULL,  url VARCHAR(500) NULL,  content TEXT NULL,  source VARCHAR(45) NULL,  postdate DATETIME NULL, gonggam INT NULL, commentCount INT NULL, PRIMARY KEY (id), UNIQUE INDEX url_UNIQUE (url ASC)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci;"
            db_connection.execute(sql)
            print('create table')
        except:
            print('', end='')

        sql = "SELECT count(*) FROM Crawl_blog WHERE url = %s"
        result = db_connection.execute(sql, (url))
        result = (result.first()[0])
        if result > 0:
            print(i, ': ', url, ' skip')
        else:
            if 'naver' in url:
                src = 'naver_blog'
                content, gong, cmt = naver(driver, url)
            elif 'daum' in url:
                src = 'daum_blog'
                content = ('daum')
                gong = 0
                cmt = 0
            else:
                src = 'etc'
                content = ('기타')
                gong = 0
                cmt = 0

            time.sleep(random.uniform(2, 4))
            sql = "INSERT INTO Crawl_blog (query, url, content, source, postdate, gonggam, commentCount) VALUES (%s, %s, %s, %s, %s, %s, %s)"

            try:
                db_connection.execute(sql, (query, url, content, src, df['postdate'][i], gong, cmt))
            except:
                db_connection.execute(sql, (query, url, '특수문자_인식불가', src, df['postdate'][i], gong, cmt))

            print(i, ': ', url, ' done')


def YOUTUBE_Cralwer(query):
    list_youtube, urls = request_youtube(query)
    content_youtube = get_video_comments(query)