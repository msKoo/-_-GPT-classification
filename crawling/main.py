import time
from collections import OrderedDict
from crawling.Crawling_modules import BLOG_Crawler, YOUTUBE_Cralwer
from crawling.Get_Database import get_blog_url, get_youtube, get_today_youtube, get_today_blog
from crawling.openApi.Naver_blog import url_naver
from crawling.openApi.Daum_blog import url_daum

#각 도메인 별, 크롤링한 정보 dict 형태로 저장
def returnDict(keyword, source, duration):
    week = OrderedDict()
    halfDuration = int(duration / 2)

    #네이버 블로그, 다음 블로그, 다음 카페 => 함수

    if source == "youtube":
        value, date = get_today_youtube(keyword, duration)
        # print(value, date)
    else:
        value, date = get_today_blog(keyword, source, duration)
    lenList = list(map(lambda x: len(x), date))

    percentage = sum(lenList[:halfDuration]) - sum(lenList[halfDuration: ])

    week['domain'] = source
    week['value'] = sum(lenList[:halfDuration]) # 이번 주 리뷰 갯수
    # week['value'] = value  # 이번 주 리뷰 갯수
    week['percentage'] = abs(percentage) #저번주 - 이번주의 절대값
    week['increase'] = True if percentage >= 0 else False # 증가인지 감소인지
    week['data'] = lenList[:halfDuration] #이번 주 리뷰 data

    return week


def reviewData(list):
    result = OrderedDict()
    errorWord = "해당 데이터가 존재하지 않습니다."

    newList = sorted(list, key=lambda x: x['value'], reverse=True)

    # list.sort(key=lambda x: x['value'], reverse=True)
    mostReviewDomain = errorWord if not newList else newList[0]["domain"]
    result["mostReviewDomain"] = mostReviewDomain

    increaseItem = [item for item in newList if item['increase'] == True]
    increaseItem.sort(key=lambda x: x['percentage'], reverse=True)
    increaseReviewDomain = errorWord if not increaseItem else increaseItem[0]["domain"]
    result["increaseReviewDomain"] = increaseReviewDomain

    decreaseItem = [item for item in newList if item['increase'] == False]
    decreaseItem.sort(key=lambda x: x['percentage'], reverse=True)
    decreaseReviewDomain = errorWord if not decreaseItem else decreaseItem[0]["domain"]
    result["decreaseReviewDomain"] = decreaseReviewDomain

    totalList = [item["value"] for item in newList]
    totalToday = errorWord if not newList else sum(totalList)
    result["totalToday"] = totalToday

    return result


def getReviewRealTime(keyword, duration):
    result = []
    # 7일 동안 value
    # 이전 7일 과 금주 차이
    # 차이에 따른 increase 유무
    # data = 7일간 출력

    #실시간 크롤링 가능 도메인 목록
    source_type = ['naver_blog', 'youtube', 'daum_blog', 'daum_cafe']
    for type in source_type:
        # 값을 읽어와 리스트에 삽입
        result.append(returnDict(keyword, type, duration))
    # result.sort(key=lambda x:x['domain'])\
    reviewAnalysisData = reviewData(result)
    result.append(reviewAnalysisData)

    return result

