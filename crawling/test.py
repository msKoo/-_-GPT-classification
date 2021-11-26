import time
from collections import OrderedDict
from crawling.Crawling_modules import BLOG_Crawler, YOUTUBE_Cralwer
from crawling.Get_Database import get_blog_url, get_youtube, get_today_youtube, get_today_blog

def getReviewRealTime(keyword, duration):
    reslut = OrderedDict()
    #7일 동안 value
    #이전 7일 과 금주 차이
    #차이에 따른 increase 유무
    #data = 7일간 출력

    #네이버 블로그
    value, date = get_today_blog(keyword, duration)

    print(value)
    print(len(date[0]) - len(date[1]))

    #유튜브 댓글
    value, date = get_today_youtube(keyword, duration)

    print(value)
    print(len(date[0]) - len(date[1]))



    return 'test'