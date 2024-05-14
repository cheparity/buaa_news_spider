import time
from urllib.parse import quote_plus, quote

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tools import *

UA_LIST = get_data(file_path="meta/user_agents.txt")
BUAA_NEWS_WEB_URL = 'https://ev.buaa.edu.cn/News___Events/News.htm'


class Spider:
    def __init__(self):
        self.driver = init_firefox_driver()
        self.logger = MyLogger(name="Spider",
                               output_path=f"./data/log/spider.log")
        self.results_set = set()

    def click_next_btn(self):
        try:
            next_btn = self.driver.find_element(
                By.CSS_SELECTOR, "html body div.main div.page2 div.warp div.con div.pb_sys_common.pb_sys_normal.pb_sys_style1 span.p_pages span.p_next.p_fun a")
            # 如果不可以点击，返回False
            if "javascript:void(0)" in next_btn.get_attribute("href"):
                return False
            # 否则点击
            next_btn.click()
            time.sleep(5)
            return True
        except Exception as e:
            self.logger.info(f"Error when clicking the next-page button: {e}")
            return False

    def get_result_from_soup(self):
        page = self.driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        # 选择xpath为NEWS_GUSTER_XPAHT的元素
        news_guster = soup.select('li.cf')
        self.logger.info(f"Got {len(news_guster)} news-guster")
        for a in news_guster:  # a jsname="UWckNb"
            try:
                url = a.find("a").get("href") # type: ignore
                # url: '../info/1012/12345.htm'
                url = "https://ev.buaa.edu.cn" + url[2:] # type: ignore
                title = a.find("a").attrs["title"] # type: ignore
                self.logger.info(f"Got one result:{url}, {title}")
                yield [title, url]
            except Exception as e:
                self.logger.warning(f"Error occured when parsing divs: {e}")
                save_as_csv([self.driver.current_url],
                            file_path=f"data/progress_of_{quote(self.question)}.csv") # type: ignore

    def catch_results(self):
        results = self.get_result_from_soup()
        for result in results:
            self.results_set.add(tuple(result))

    def run(self):
        self.logger.info("=====start to run=====")
        self.logger.info("url: " + BUAA_NEWS_WEB_URL)
        self.driver.get(BUAA_NEWS_WEB_URL)
        self.logger.info("=====start to catch results in page=====")
        self.catch_results()
        while self.click_next_btn():
            self.catch_results()
        self.logger.info(f"Get {len(self.results_set)} results in total")
        # save
        save_as_csv(self.results_set, file_path="data/buaa_news.csv")
        self.logger.info("=====end to catch results in page=====")
        self.driver.quit()
        return self.results_set


if __name__ == '__main__':
    Spider().run()
