from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import copy

class Cosine_Similarity:
    def __init__(self, excelDF, row):

        """
        TF IDF 를 이용한  Cosine 유사도 판별
        excelDf : 유사도를 측정할 대상 문장 excel
        text : 유사도를 측정할 문장
        """

        self.excelDF = excelDF
        self.row = row
        self.setQuestion()  # question 벡터화를 위한 question 리스트

    # question 초기화 함수
    def setQuestion(self):
        question = []

        df = self.excelDF[self.row]
        #결측치 제거 작업 필요
        for i, x in enumerate(df):
            if pd.isna(x):
                question.append('None')
            else:
                question.append(x)
        self.questionList = question

        # print(question)



        # df_np = pd.DataFrame.to_numpy(self.excelDF)
        # for i in range(len(df_np)):
        #     question.append(df_np[i][4])
        # self.questionList = question
        # print(question)

    def vecotrization(self, text):  # 벡터화

        ## 후에 DB에서 해당 벡터요소를 가져오는 작업 추가

        # 문제점 : 객체 생성 후 대상 리스트를 두번 생성 ( 메모리 낭비 )

        # 나중에 유사도 판별 시 : 생성한 문장을 포함하려면 밑의 방식

        vectorizer = TfidfVectorizer()
        TFIDF_matrix = copy.deepcopy(self.questionList)  # 리스트 깊은 복사 수행
        TFIDF_matrix.append(text)  # 리스트에 추가
        text_matrix = vectorizer.fit_transform(TFIDF_matrix)  # 벡터화 실시

        return text_matrix

    def get_similarity(self, text):
        """
        nex_matrix : 원고 문장을 벡터화 한 리스트에 해당 문장을 추가한 리스트를 백터화
        nex_matrix[-1] : text 벡터화 정보
        nex_matrix[:-1] : text를 제외한 원고 문장 벡터 정보
        """
        new_matrix = self.vecotrization(text)  # 새로운 벡터 메트릭스 생성

        cosine_sim = cosine_similarity(new_matrix[-1], new_matrix[:-1])  # 코사인 유사도 계산
        del new_matrix #워드 벡터화 삭제

        #sim_score의 인덱스 붙이기
        sim_scores = list(enumerate(cosine_sim[-1]))

        # 유사도에 따라질문들을 정렬.
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # 가장 유사한 5개의 질문의 인덱싱 추출
        sim_scores = sim_scores[:5]

        # 유사도와, 원본 문장 list 생성
        cos_result = [(self.excelDF[self.row].iloc[i[0]],round(i[1],3)) for i in sim_scores]

        return cos_result

def getSimilarity(text):
    path = "./service/origin/ver1.xlsx"
    row = 'sentense'

    df = pd.read_excel(path)

    s = Cosine_Similarity(df, row)
    a = s.get_similarity(text)

    return a

