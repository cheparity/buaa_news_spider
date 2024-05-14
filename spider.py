import time  # 导入时间模块，用于处理时间相关的操作
from urllib.parse import quote_plus, quote  # 导入URL编码相关的函数

from bs4 import BeautifulSoup  # 导入BeautifulSoup库，用于解析HTML内容
from selenium.webdriver.common.by import By  # 导入By模块，用于定位页面元素
from selenium.webdriver.support import expected_conditions as EC  # 导入期望条件模块
from selenium.webdriver.support.ui import WebDriverWait  # 导入WebDriverWait模块，用于显式等待

from tools import *  # 导入tools模块中的所有函数

# 获取用户代理列表
UA_LIST = get_data(file_path="meta/user_agents.txt")
# 北航新闻网页的URL
BUAA_NEWS_WEB_URL = 'https://ev.buaa.edu.cn/News___Events/News.htm'


# 定义一个爬虫类
class Spider:
    def __init__(self):
        # 初始化Firefox浏览器驱动
        self.driver = init_firefox_driver()
        # 初始化日志记录器
        self.logger = MyLogger(name="Spider",
                               output_path=f"./data/log/spider.log")
        # 初始化结果集合，用于存储抓取到的结果
        self.results_set = set()

    # 定义点击下一页按钮的方法
    def click_next_btn(self):
        try:
            # 找到页面上的“下一页”按钮
            next_btn = self.driver.find_element(
                By.CSS_SELECTOR, "html body div.main div.page2 div.warp div.con div.pb_sys_common.pb_sys_normal.pb_sys_style1 span.p_pages span.p_next.p_fun a")
            # 如果按钮不可点击，返回False
            if "javascript:void(0)" in next_btn.get_attribute("href"):
                return False
            # 否则点击按钮
            next_btn.click()
            # 等待5秒，确保页面加载完成
            time.sleep(5)
            return True
        except Exception as e:
            # 记录点击下一页按钮时的错误
            self.logger.info(f"Error when clicking the next-page button: {e}")
            return False

    # 定义从页面解析结果的方法
    def get_result_from_soup(self):
        # 获取页面的源代码
        page = self.driver.page_source
        # 使用BeautifulSoup解析页面
        soup = BeautifulSoup(page, "html.parser")
        # 选择页面上的新闻条目
        news_guster = soup.select('li.cf')
        self.logger.info(f"Got {len(news_guster)} news-guster")
        # 遍历每个新闻条目
        for a in news_guster:  # a jsname="UWckNb"
            try:
                # 获取新闻链接
                url = a.find("a").get("href")  # type: ignore
                # 拼接完整的URL
                url = "https://ev.buaa.edu.cn" + url[2:]  # type: ignore
                # 获取新闻标题
                title = a.find("a").attrs["title"]  # type: ignore
                self.logger.info(f"Got one result:{url}, {title}")
                # 生成一个包含标题和URL的列表
                yield [title, url]
            except Exception as e:
                # 记录解析新闻条目时的错误
                self.logger.warning(f"Error occured when parsing divs: {e}")
                save_as_csv([self.driver.current_url],
                            file_path=f"data/progress_of_{quote(self.question)}.csv")  # type: ignore

    # 定义捕获结果的方法
    def catch_results(self):
        # 获取解析结果
        results = self.get_result_from_soup()
        # 将结果添加到结果集合中
        for result in results:
            self.results_set.add(tuple(result))

    # 定义运行爬虫的方法
    def run(self):
        self.logger.info("=====start to run=====")
        self.logger.info("url: " + BUAA_NEWS_WEB_URL)
        # 打开新闻页面
        self.driver.get(BUAA_NEWS_WEB_URL)
        self.logger.info("=====start to catch results in page=====")
        # 捕获当前页面的结果
        self.catch_results()
        # 循环点击下一页按钮并捕获结果，直到没有下一页
        while self.click_next_btn():
            self.catch_results()
        self.logger.info(f"Get {len(self.results_set)} results in total")
        # 保存结果到CSV文件
        save_as_csv(self.results_set, file_path="data/buaa_news.csv")
        self.logger.info("=====end to catch results in page=====")
        # 关闭浏览器
        self.driver.quit()
        # 返回结果集合
        return self.results_set


# 程序的入口，运行爬虫
if __name__ == '__main__':
    Spider().run()
