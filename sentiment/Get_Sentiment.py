import configparser
import pymysql

import pandas as pd
import ast

from sqlalchemy import create_engine

from sentiment.Morph.KNU import senti_Anal
from sentiment.Morph.getMorph import getCorpus_Khaiii

from crawling.Get_Database import get_blog_content, get_youtube
import json

from service.reputation_service import detailed_sentiment

import numpy as np

import tensorflow as tf

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def analysis_morph(query,source):

    db_connection_str = config['MYSQL_CONFIG']['db_connection']
    db_connection = create_engine(db_connection_str)

    # id_, content_, url_, source_= get_youtube(query)

    # id += id_
    # content += content_
    # url += url_
    # source += source_

    mc = []
    if source == 'naver_blog':
        print('크롤링 및 감성 분석 진행중-- naver_blog :', query)
        id, content, postdate, url, source = get_blog_content(query)
        try:
            sql = "CREATE TABLE sentimentAnal ( id INT NOT NULL AUTO_INCREMENT ,  content TEXT NULL, postdate DATETIME NULL, url VARCHAR(500) NULL, query VARCHAR(45) NULL,  source VARCHAR(45) NULL,  sentiAnal TEXT NULL, PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci;"
            db_connection.execute(sql)
            print('create table')
        except:
            print('', end='')
        for i, corpus in (enumerate(content)):
            print(query,' ; ', len(content),'중 ',i,'번째')
            sql = "SELECT count(*) FROM sentimentAnal WHERE url = %s"
            result = db_connection.execute(sql, url[i])
            result = (result.first()[0])
            if result > 0:
                print(i, ': ', url[i], ' skip')
            else:
                sql = "INSERT INTO sentimentAnal (content, postdate, url, query, source, sentiAnal) VALUES (%s, %s,  %s, %s, %s, %s)"
                dic = {}
                try:
                    if (len(corpus) < 20000):   # 2만 글자 이상은 제외
                        document = getCorpus_Khaiii(corpus)
                        for sentence in document:
                            for phrase in sentence:
                                for word in phrase:
                                    senti_score = senti_Anal(word[0])
                                    # print(word[0],':',senti_score)
                                    if (senti_score != 'None'):
                                        dic[word[0]] = senti_score
                        mc.append(dic)
                    else:
                        print("too long", end="/ ")
                        continue
                except:
                    # mc.append(dic)
                    print("외국어 or Too long", end="/ ")
                    continue
                db_connection.execute(sql, (corpus, postdate[i].strftime("%Y%m%d"), url[i], query, source[i], json.dumps(dic, ensure_ascii = False)))
                print(i, ': ', url[i], ' done')
    elif 'youtube' in source:
        print('크롤링 및 감성 분석 진행중-- youtube_comment :', query)
        id, content, postdate, url, source = get_youtube(query)
        try:
            sql = "CREATE TABLE sentimentAnal_youtube ( id INT NOT NULL AUTO_INCREMENT ,  content TEXT NULL, postdate DATETIME NULL, url VARCHAR(500) NULL, query VARCHAR(45) NULL,  source VARCHAR(45) NULL,  sentiAnal TEXT NULL, PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci;"
            db_connection.execute(sql)
            print('create table')
        except:
            print('', end='')

        for i, corpus in (enumerate(content)):
            print(len(content), '중 ', i, '번째')
            sql = "SELECT count(*) FROM sentimentAnal_youtube WHERE content = %s"
            result = db_connection.execute(sql, corpus)
            result = (result.first()[0])
            if result > 0:
                print(i, ': ', url[i], ' skip')
            else:
                sql = "INSERT INTO sentimentAnal_youtube (content, postdate, url, query, source, sentiAnal) VALUES (%s, %s,  %s, %s, %s, %s)"

                dic = {}
                try:
                    document = getCorpus_Khaiii(corpus)
                    for sentence in document:
                        for phrase in sentence:
                            for word in phrase:
                                senti_score = senti_Anal(word[0])
                                # print(word[0],':',senti_score)
                                if (senti_score != 'None'):
                                    dic[word[0]] = senti_score
                    mc.append(dic)
                except:
                    # mc.append(dic)
                    print("외국어 or Too long", end="/ ")
                    continue
                db_connection.execute(sql, (
                corpus, postdate[i].strftime("%Y%m%d"), url[i], query, source[i], json.dumps(dic, ensure_ascii=False)))
                print(i, ': ', url[i], ' done')


def analysisSentence(corpus):
    document = getCorpus_Khaiii(corpus)
    # print('first:',document[0][0][0])  # first: ('청주', 'NNP')
    for sentence in document:
        for phrase in sentence:
            for word in phrase:
                senti_score = senti_Anal(word[0])
                print(word[0], '/', senti_score)
    return document


def insert_sentence_senti_detail_column(source):
    conn = pymysql.connect(
        host=config['MYSQL_CONFIG']['sql_host'],
        user=config['MYSQL_CONFIG']['user'],
        password=config['MYSQL_CONFIG']['password'],
        db=config['MYSQL_CONFIG']['db'],
        charset=config['MYSQL_CONFIG']['charset']
    )
    curs = conn.cursor()

    try:
        if 'youtube' in source:
            sql = "select id, content from sentimentAnal_youtube"
            curs.execute(sql)
            rows = curs.fetchall()
            content = []
            for row in rows:
                content.append(row[1])
            repu, value = (detailed_sentiment(content))
            repu = np.array(value)
            for i, row in enumerate(rows):
                id = row[0]
                sql = "update sentimentAnal_youtube set sentiAnal_detail = %s where id = %s"
                if repu[i] == 0:
                    result = '기쁨'
                elif repu[i] == 1:
                    result = '불안'
                elif repu[i] == 2:
                    result = '당황'
                elif repu[i] == 3:
                    result = '슬픔'
                elif repu[i] == 4:
                    result = '분노'
                elif repu[i] == 5:
                    result = '상처'
                # print(sql, result, (id))
                curs.execute(sql, (result, id))
        else:
            sql = "select id, content, url from sentimentAnal"
            curs.execute(sql)
            rows = curs.fetchall()
            content = []
            for row in rows:
                content.append(row[1])
            repu = (detailed_sentiment(content))
            repu = np.array(repu)
            for i, row in enumerate(rows):
                url = row[2]
                sql = "update sentimentAnal set sentiAnal_detail = %s where url = %s"
                if repu[i] == 0:
                    result = '기쁨'
                elif repu[i] == 1:
                    result = '불안'
                elif repu[i] == 2:
                    result = '당황'
                elif repu[i] == 3:
                    result = '슬픔'
                elif repu[i] == 4:
                    result = '분노'
                elif repu[i] == 5:
                    result  = '상처'
                print(result)
                curs.execute(sql, (result, url))

    except Exception as e:
        print(e)
        conn.close()
        return False

    conn.commit()
    conn.close()

    return True


# def change_form():
#     df = pd.read_excel('src/train_phraseSent.excel')
#     datas = df['phraseSent'].values.tolist()
#
#     result = []
#     for data in datas:
#         data = ast.literal_eval(data)
#         content_size = len(datas)
#         content_value = [[] for _ in range(content_size)]
#         for i, content in enumerate(data):
#             for morph in content:
#                 morph = morph.split('/')
#                 if morph[1] == 'None':
#                     continue
#                 content_value[i].append(morph[1])
#         result.append(content_value[i])
#     print(result)
#     return content_value