import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import configparser
import time
from bs4 import BeautifulSoup

# from pyvirtualdisplay import Display

class Chrome_Naver():
    def __init__(self, query, start, end):
        config = configparser.ConfigParser()
        config.read('../config.ini', encoding='utf-8')
        config.sections()

        self.options = Options()

        self.query = query
        # self.date = staradd_argumentt + "to" + end
        self.options.add_argument('user-agent='+ "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36")
        # self.options.add_argument('headless')  # headless 모드 브라우저가 뜨지 않고 실행됩니다.
        self.options.add_argument('--window-size= 360, 360')  # 실행되는 브라우저 크기를 지정할 수 있습니다.
        self.options.add_argument('--blink-settings=imagesEnabled=false')  # 브라우저에서 이미지 로딩을 하지 않습니다.
        # self.options.add_argument("--proxy-server=socks5://127.0.0.1:9050")
        # self.driver = webdriver.Chrome(executable_path="/Users/koomisong/PycharmProjects/평판관리/Crawler/chromedriver", options=options)

        self.Crawl_Naver_blog()
        # self.Crawl_Naver_cafe()
        self.quit_driver()

    def Crawl_Naver_blog(self):
        # display = Display(visible=0, size=(1920, 1080))
        # display.start()
        # path = '/home/drsong/download/chromedriver'    # linux server

        # conda python
        path = '/Users/koomisong/PycharmProjects/평판관리/Crawler/chromedriver'
        self.driver = webdriver.Chrome(executable_path=path,
                                       options=self.options)

        df = pd.read_excel('Crawler/Crawling_Result/URL_DATA/' + self.query + '_Naver_blog.xlsx')
        id = df['id'].values.list()
        postdate = df['postdate'].values.tolist()
        source = df['source'].values.tolist()
        url_list = df['url'].values.tolist()
        title_list = df['title'].values.tolist()

        title = []
        content_blog = []
        gonggam = []
        commentCount = []

        for i, url in enumerate(url_list) :
            if url.startswith("https://blog.naver.com"):
                self.driver.get(url)
                self.driver.implicitly_wait(1)
                self.driver.switch_to.frame("mainFrame")
                self.driver.implicitly_wait(1)

                req = self.driver.page_source
                soup = BeautifulSoup(req, 'html.parser')

                title.append(title_list[i])

                if soup.find("div", attrs={"class": "se-main-container"}):  # se-component se-video se-l-default 제외
                    text = soup.find("div", attrs={"class": "se-main-container"})
                    if soup.find("div", attrs={"class": "se-component se-video se-l-default"}):
                        unwanted = text.find("div", attrs={"class": "se-component se-video se-l-default"})
                        unwanted.decompose()
                    text = text.get_text()
                    text = text.replace("\n", "").replace("\u200b", "").replace("​", "").replace(" ", "")  # 공백 제거
                    content_blog.append(text)
                elif soup.find("div", attrs={"id": "postViewArea"}):
                    text = soup.find("div", attrs={"id": "postViewArea"}).get_text()
                    text = text.replace("\n", "")  # 공백 제거
                    content_blog.append(text)
                elif soup.find("div", attrs={"id": "postListBody"}):
                    text = soup.find("div", attrs={"id": "postListBody"}).get_text()
                    text = text.replace("\n", "")  # 공백 제거
                    content_blog.append(text)
                else:
                    print("본문 없음")
                    content_blog.append('none')

                if soup.find("em", attrs={"class": "u_cnt _count", "style": "display: none;"}) :
                    text = soup.find("em", attrs={"class": "u_cnt _count", "style": "display: none;"})  #
                    # print(text)
                    try:
                        gonggam.append((int(text.get_text())))
                    except:
                        gonggam.append(0)
                elif soup.find("em", attrs={"class": "u_cnt _count"}):
                    text = soup.find("em", attrs={"class": "u_cnt _count"})
                    # print(text)
                    try:
                        gonggam.append((int(text.get_text())))
                    except:
                        gonggam.append(0)
                else:
                    print("공감 요소 없음")
                    gonggam.append('none')

                if soup.find("em", attrs={"class": "_commentCount"}):  # null일 경우 0
                    text = soup.find("em", attrs={"class": "_commentCount"})
                    try:
                        commentCount.append(int(text.get_text()))
                    except:
                        commentCount.append(0)
                else:
                    print("댓글 요소 없음")
                    commentCount.append('none')
            else:
                title.append("not naver")
                content_blog.append("not naver")
                gonggam.append("not naver")
                commentCount.append("not naver")

            time.sleep(random.uniform(2,4))
            print(i, ': ',url,' done')
            if i == 999:
                break
        self.to_excel(id, content_blog, source, postdate)

    def Crawl_Naver_cafe(self):
        url_list = []
        title_list = []
        date_list = []
        url = "https://search.naver.com/search.naver?where=article&sm=tab_viw.blog&query="+self.query+"&nso="
        self.driver.get(url)

        class_href = ".api_txt_lines.total_tit"  # 제목, 링크 가져오기

        while True:
            prev_height = self.driver.execute_script("return document.body.scrollHeight")
            # 스크롤을 화면 가장 아래로 내린다
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            # 페이지 로딩 대기
            time.sleep(1)
            # 현재 문서 높이를 가져와서 저장
            curr_height = self.driver.execute_script("return document.body.scrollHeight")

            if (curr_height == prev_height):
                break
            else:
                prev_height = self.driver.execute_script("return document.body.scrollHeight")

        for article in self.driver.find_elements(By.CSS_SELECTOR, class_href):
            url = article.get_attribute('href')
            url_list.append(url)
            title = article.text
            title_list.append(title)

        for article in self.driver.find_elements(By.CLASS_NAME, "sub_time.sub_txt") :
            date_list.append(article.text)

        self.to_excel(title_list, url_list, 'cafe')


    def to_excel(self, id,content, source, postdate):
        df = pd.DataFrame(
            {'id':id, 'keyword': self.query, 'content': content, 'source': source, 'postdate': postdate})
        df.to_excel('Crawler/Crawling_Result/CONTENT_DATA/' + self.query + '_Naver_blog.xlsx', index=False)

    def quit_driver(self):
        self.driver.close()

def naver(driver, url):
    try:
        driver.get(url)
        driver.implicitly_wait(1)
        driver.switch_to.frame("mainFrame")
        driver.implicitly_wait(1)

        req = driver.page_source
        soup = BeautifulSoup(req, 'html.parser')

        if soup.find("div", attrs={"class": "se-main-container"}):  # se-component se-video se-l-default 제외
            text = soup.find("div", attrs={"class": "se-main-container"})
            if soup.find("div", attrs={"class": "se-component se-video se-l-default"}):
                unwanted = text.find("div", attrs={"class": "se-component se-video se-l-default"})
                unwanted.decompose()
            text = text.get_text()
            text = text.replace("\n", "").replace("\u200b", "").replace("​", "").replace(" ", "")  # 공백 제거
            # content_blog.append(text)
            content_blog = text
        elif soup.find("div", attrs={"id": "postViewArea"}):
            text = soup.find("div", attrs={"id": "postViewArea"}).get_text()
            text = text.replace("\n", "")  # 공백 제거
            # content_blog.append(text)
            content_blog = text
        elif soup.find("div", attrs={"id": "postListBody"}):
            text = soup.find("div", attrs={"id": "postListBody"}).get_text()
            text = text.replace("\n", "")  # 공백 제거
            # content_blog.append(text)
            content_blog = text
        else:
            print("본문 없음")
            # content_blog.append(text)
            content_blog = 'none'

        if soup.find("em", attrs={"class": "u_cnt _count", "style": "display: none;"}):
            text = soup.find("em", attrs={"class": "u_cnt _count", "style": "display: none;"})  #
            # print(text)
            try:
                # gonggam.append((int(text.get_text())))
                gonggam = (int(text.get_text()))
            except:
                # gonggam.append(0)
                gonggam = 0
        elif soup.find("em", attrs={"class": "u_cnt _count"}):
            text = soup.find("em", attrs={"class": "u_cnt _count"})
            # print(text)
            try:
                # gonggam.append((int(text.get_text())))
                gonggam = (int(text.get_text()))
            except:
                # gonggam.append(0)
                gonggam = 0
        else:
            print("공감 요소 없음")
            # gonggam.append('none')
            gonggam = 0

        if soup.find("em", attrs={"class": "_commentCount"}):  # null일 경우 0
            text = soup.find("em", attrs={"class": "_commentCount"})
            try:
                # commentCount.append(int(text.get_text()))
                commentCount = int(text.get_text())
            except:
                # commentCount.append(0)
                commentCount = 0
        else:
            print("댓글 요소 없음")
            # commentCount.append('none')
            commentCount = 0
    except:
        content_blog = 'none'
        gonggam = 0
        commentCount = 0

    return content_blog, gonggam, commentCount