from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd

# https://www.lambdatest.com/blog/selenium-safaridriver-macos/
# https://datart.tistory.com/28 : 각 URL 글 읽어오기

#  이 클래스는 없어도 될 듯
class Chrome_Daum():
    def __init__(self, query, start_Date, end_Date):
        options = Options()

        self.query = query
        self.start_Date = start_Date
        self.end_Date = end_Date

        options.add_argument('user-agent=' + "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36")
        # options.add_argument('headless')  # headless 모드 브라우저가 뜨지 않고 실행됩니다.
        options.add_argument('--window-size= 360, 640')  # 실행되는 브라우저 크기를 지정할 수 있습니다.
        # options.add_argument('--blink-settings=imagesEnabled=false')  # 브라우저에서 이미지 로딩을 하지 않습니다.
        options.add_argument("--proxy-server=socks5://127.0.0.1:9050")
        self.driver = webdriver.Chrome(executable_path="/Users/koomisong/PycharmProjects/평판관리/Crawler/chromedriver", options=options)

        self.Crawl_Daum_blog()
        # self.Crawl_Daum_cafe()
        self.quit_driver()

    def Crawl_Daum_blog(self):
        df = pd.read_excel('Crawler/Crawling_Result/URL_DATA/생기한의원_Daum_blog.xlsx')
        url_list = df['url'].values.tolist()
        title_list = df['title'].values.tolist()
        self.driver.get("https://blog.daum.net/saengki1925/2")
        article = []
        gonggam = []
        comment = []

        for url in url_list:
            try:  # 블로그 본문
                if url.startswith("https://blog.naver.com"):
                    article.append(self.driver.find_element(By.CLASS_NAME, "cContentBody"))
                    gonggam.append(self.driver.find_element(By.CLASS_NAME, "txt_like uoc-count"))
                    comment.append(self.driver.find_element(By.ID, "commentCount326_2"))
            except NoSuchElementException:
                return False

        print(article.text)

        # self.to_excel(title_list, url_list, 'blog')

    def Crawl_Daum_cafe(self):
        df = pd.read_excel('Crawler/Crawling_Result/URL_DATA/생기한의원_Daum_blog.xlsx')
        url_list = []
        title_list = []
        # 분당 5페이지 정도

        # url = "https://search.daum.net/search?w=cafe&DA=STC&q=" + self.query + \
        #       "&period=u&sd=" + self.start_Date + "000000&ed="+self.end_Date+"235959&p=1"
        url="https://search.daum.net/search?w=cafe&nil_search=btn&DA=NTB&enc=utf8&ASearchType=1&lpp=10&rlang=0&q="+self.query
        self.driver.get(url)

        class_href = "f_link_b"  # 제목, 링크 가져오기

        for article in self.driver.find_elements(By.CLASS_NAME, class_href):
            url = article.get_attribute('href')
            url_list.append(url)
            title = article.text
            title_list.append(title)

        self.to_excel(title_list, url_list, 'cafe')

    def to_excel(self, title_list, url_list, name):
        df = pd.DataFrame({'title': title_list, 'url': url_list})
        df.to_excel('Crawler/Crawling_Result/'+self.query+'_Daum_' + name + '_' + self.start_Date + 'to' + self.end_Date + '.xlsx', index=True, index_label = "id")

    def quit_driver(self):
        self.driver.close()

def daum(driver, url):
    driver.get(url)
    try:  # 블로그 본문
        if url.startswith("https://blog.naver.com"):
            article = (driver.find_element(By.CLASS_NAME, "cContentBody"))
            gonggam = (driver.find_element(By.CLASS_NAME, "txt_like uoc-count"))
            comment = (driver.find_element(By.ID, "commentCount326_2"))
    except NoSuchElementException:
        article

    return article, gonggam, comment