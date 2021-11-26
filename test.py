# from crawling.Crawling_modules import YOUTUBE_Cralwer, BLOG_Crawler
# from crawling.Get_Database import get_sentence_senti_detail, get_detail_boardList
# from crawling.main import returnDict
# from crawling.openApi.Naver_blog import url_naver
# from crawling.openApi.Daum_blog import url_daum
# from model.memoryContent import read_db_CorrentPast, read_db_sentimentAnal
# from sentiment.Get_Sentiment import insert_sentence_senti_detail_column

import time

# /Users/koomisong/Desktop/saso/saso_nlp=/home/drsong/web/saso_nlp

# queries = ['서울대병원', '뉴로영진', '자닮인','바른몸한의원', '비디치과', '신세계치과']
#
# for query in queries:
#     start = time.time()
#
#     print('----------openApi 및 youtube 크롤링----------')
#     # url_naver(query)
#     # url_daum(query)
#     # YOUTUBE_Cralwer(query)
#
#     print('----------블로그 본문 크롤링----------')
#     BLOG_Crawler(query)
#
#
#     print('----------크롤링 결과 감성 분석----------')
#     insert_sentence_senti_detail_column('youtube_comment')
#     analysisDB(query, 'youtube_comment')
#
#     print("소요 시간 :", time.time() - start)
#
# from service.finetuning_model.train_module import train_model_posneg
from service.reputation_service import repu_main
start = time.time()


# train_model()
# train_model_posneg()
text = "기분이 날아갈 것 같다"
repu_main(text)
# print(text, '\n 세부 감정 분석 (label : 기쁨 : 0, 불안 : 1, 당황 : 2, 슬픔 : 3, 분노 : 4, 상처 : 5) \n ->', result, ' => ', value)

print("소요 시간 :", time.time() - start)
