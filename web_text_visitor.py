import requests  # 导入requests库，用于发送网络请求
from bs4 import BeautifulSoup  # 导入BeautifulSoup库，用于解析HTML内容
from tools import *  # 从tools模块导入所有工具函数

SEPERATOR = "--------------------------------------------------\n\n\n"  # 定义分隔符，用于分隔文章内容


# 定义一个函数，用于获取网页文本
def get_web_text(url):
    response = requests.get(url)  # 发送GET请求到指定URL
    if response.status_code == 200:  # 如果请求成功（状态码为200）
        page_content = response.content.decode('utf-8')  # 获取网页内容并解码为UTF-8格式
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(page_content, "html.parser")

        # 找到所有类名为.del的元素
        del_elements = soup.select('.del')

        # 从这些元素中提取文本
        extracted_text = ""
        for element in del_elements:
            extracted_text += element.get_text()  # 获取元素的文本内容并添加到extracted_text中
        return extracted_text.strip()  # 返回提取的文本，并去掉首尾空格
    else:
        # 如果请求失败，抛出异常
        raise Exception(f"Response code: {response.status_code}")

# 定义一个类，用于访问网页


class WebVisitor:
    def __init__(self, read_from_path: str, error_web_path: str = "./data/error_webs.csv"):
        # 初始化日志记录器
        self.logger = MyLogger(
            output_path="./data/log/web_visitor_logger.log", name="WebVisitor")
        # 要读取的文件路径
        self.read_from = read_from_path
        # 记录错误网页的文件路径
        self.error_webs_path = error_web_path

    # 从文件中获取标题和URL
    def get_title_and_url(self):
        with open(self.read_from, 'r', encoding="utf-8") as f:
            reader = csv.reader(f)  # 读取CSV文件
            for row in reader:
                if len(row) == 0:  # 如果行为空，跳过
                    continue
                url = row[0]  # 获取URL
                title = row[1] if len(row) == 2 else "".join(row[1:])  # 获取标题
                yield title, url  # 返回标题和URL

    # 将网页文本写入文件
    def write_web_text_in_file(self, write_to_path: str = "./data/web_text.txt"):
        with open(write_to_path, 'a', encoding="utf-8") as f:
            article_cnt = 1  # 文章计数器
            for title, url in self.get_title_and_url():
                self.logger.info(f"Parsing web: {title},{url}")  # 记录日志信息
                try:
                    web_text = get_web_text(url)  # 获取网页文本
                    f.write(
                        f"ARTICLE_ID:{article_cnt}\nTITLE:{title}\nURL:{url}\nTEXT:\n{web_text}\n{SEPERATOR}"
                    )  # 将文章ID、标题、URL和文本写入文件
                    article_cnt += 1  # 增加文章计数器
                except Exception as e:
                    # 记录错误信息
                    error_data = [title, url]
                    with open(self.error_webs_path, "a", encoding="utf-8") as f_error:
                        csv.writer(f_error).writerow(error_data)  # 将错误数据写入文件
                    self.logger.warning(
                        f"Error occured when parsing web. {error_data}, {e}")
                    continue


# 程序入口
if __name__ == '__main__':
    # 请替换为您要过滤的文件名
    file_to_parse = [
        "./data/buaa_news.csv",
    ]
    for file in file_to_parse:
        # 创建WebVisitor对象并调用方法处理文件
        WebVisitor(read_from_path=file).write_web_text_in_file()
