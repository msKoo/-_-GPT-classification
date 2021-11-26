from collections import OrderedDict

from model.memoryContent import sortByFrequency, make_listDict, pathTest
from crawling.main import getReviewRealTime
from crawling.Get_Database import get_recent_boardList, get_sentence_senti_detail, get_detail_boardList


#빈도수 기준 정렬
def SortingByFrequency(dict_list):
    result = []
    c = sortByFrequency(dict_list)
    dict_list = sorted(c.items(), key=lambda x: x[1], reverse=True)

    sorted_list = dict_list[:10]
    for i, x in enumerate(sorted_list):
        item = {}
        item['title'] = x[0]
        item['value'] = x[1]
        result.append(item)

    return result

#달별 감상단어출력 횟수
def EachMonthPosNeg(cur, pas):
    #이번 달 기준
    result = []
    currentData = OrderedDict()
    pastData = OrderedDict()

    currentData['label'] = "Current Month"
    currentData['fill'] = "start"
    currentData['pos_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
    currentData['neg_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
    currentData['nue_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]

    pastData['label'] = "Past Month"
    pastData['fill'] = "start"
    pastData['pos_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
    pastData['neg_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
    pastData['nue_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]


    cur_date = []
    cur_senti = []

    for data in cur:
        cur_date.append(data[2].strftime("%Y%m%d"))
        cur_senti.append(data[6])

    cur_date = (list(map(lambda s : s[4:6],cur_date)))
    cur_senti = make_listDict(cur_senti)

    for i, senti in enumerate(cur_senti):
        values = senti.values()
        for val in values:
            if int(val) > 0:
                currentData['pos_data'][int(cur_date[i])-1] += 1
            elif int(val) < 0:
                currentData['neg_data'][int(cur_date[i])-1] += 1
            else:
                currentData['nue_data'][int(cur_date[i])-1] += 1

    pas_date = []
    pas_senti = []

    for data in cur:
        pas_date.append(data[2].strftime("%Y%m%d"))
        pas_senti.append(data[6])
    pas_date = (list(map(lambda s: s[4:6], pas_date)))
    pas_senti = make_listDict(pas_senti)
    #
    for i, senti in enumerate(pas_senti):
        values = senti.values()
        for val in values:
            if int(val) > 0:
                pastData['pos_data'][int(pas_date[i])-1] += 1
            elif int(val) < 0:
                pastData['neg_data'][int(pas_date[i])-1] += 1
            else:
                pastData['nue_data'][int(pas_date[i])-1] += 1

    result.append(currentData)
    result.append(pastData)
    return result

# 전체 긍 부정 비율
def TotalPosNegRatio(dict_list):
    result = OrderedDict()
    num_list = countPosNegword(dict_list)
    Sum = sum(num_list) #전체 합
    if Sum != 0:
        PosNegMidRatioList = list(map(lambda x : x / Sum * 100, num_list)) #비율 계산
        data_list = [round(item,2) for item in PosNegMidRatioList]
    else:
        data_list = [0,0,0]
    result['data'] = data_list
    result['labels'] = ['긍정', '부정', '중립']

    return result

#도메인 별 리뷰 수 추이
def eachDomainReviewCount(keyword):
    #실시간 크롤링 가능한 도메인 네이버블로그, 유튜브 댓글
    # 14일 기준, 이전 7일은 금 주 7일과 비교를 위한 비교값
    DURATION = 180
    return getReviewRealTime(keyword, duration=DURATION)



def countPosNegword(items): #긍부정 단어 개수 계산
    pos, neg, mid = 0, 0, 0
    for item in items:
        value_item = item.values()
        for value in value_item:
            value = int(value)
            if value > 0:
                pos += 1
            elif value < 0:
                neg += 1
            else:
                mid += 1
    num_list = [item for item in (pos, neg, mid)]
    return num_list

#리뷰리스트 가져오기
def getReviewList(keyword):
    reviewList = []
    result = []
    source_type = ['naver_blog']
    for type in source_type:
        try:
            reviewList += get_recent_boardList(keyword, type, 5)
            # reviewList += get_sentence_senti_detail(keyword, type, '부정', 5)
        except:
            continue
    #
    print(reviewList[:5])
    for i, review in enumerate(reviewList[:5]):
        content = OrderedDict()
        content["id"] = i
        content["date"] = review[4].strftime("%Y-%m-%d")
        content["author"] = {"name":review[7], "url":review[5]}
        content["post"] = {"title":review[1]}
        content["body"] = review[2]

        result.append(content)

    return result

def getDetailList(keyword, detail):
    reviewList = []
    result = []
    source_type = ['youtube_comment']

    for type in source_type:
        try:
            reviewList += get_detail_boardList(keyword, type, detail, 5)
            # reviewList += get_sentence_senti_detail(keyword, type, '부정', 5)
        except:
            continue

        if 'youtube' in type:
            for i, review in enumerate(reviewList[:5]):
                content = OrderedDict()
                content["id"] = i
                content["date"] = review[2].strftime("%Y-%m-%d")
                content["author"] = {"name": review[4], "url": 'https://www.youtube.com/watch?v='+review[3]}
                content["post"] = {"title": review[8]}
                content["body"] = review[1]
                result.append(content)

    return result


#최종 request body
def request_body(keyword):
    result = OrderedDict()
    if keyword == 'ㅅㅇㄷㅂㅇ':
        keyword = '서울대병원'
    try:
        dict_list, cur, pas = pathTest(keyword, 'youtube_comment')
        try:
            dict_list_, cur_, pas_ = pathTest(keyword, 'naver_blog')
            dict_list += dict_list_
            cur += cur_
            pas += pas_
        except:
            print('naver 없음')
    except:
        keyword = "자닮인"
        dict_list, cur, pas = pathTest(keyword, 'naver_blog')

    orderedWord = SortingByFrequency(dict_list)
    eachMonthPosNeg = EachMonthPosNeg(cur, pas)
    totalPosNeg = TotalPosNegRatio(dict_list)
    domainReviewCount = eachDomainReviewCount(keyword)
    # reviewList = getReviewList(keyword)
    reviewList = getDetailList(keyword, '분노')

    result['orderedWord'] = orderedWord #전체 게시글 단어의 빈도수 기준 정렬
    result['eachMonthPosNeg'] = eachMonthPosNeg #저번달, 이번달 긍부정 단어 추이
    result['totalPosNeg'] = totalPosNeg #전체 단어 긍, 부정 중립 비율
    result['domainReviewCount'] = domainReviewCount #도메인별 리뷰 수
    result['reviewList'] = reviewList #리뷰 리스트

    return result


