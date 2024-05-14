import requests
from bs4 import BeautifulSoup

from tools import *

SEPERATOR = "--------------------------------------------------\n\n\n"


def get_web_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        page_content = response.content.decode('utf-8')
        soup = BeautifulSoup(page_content, "html.parser")

        # Find the .del elements
        del_elements = soup.select('.del')

        # Extract the text from del_elements
        extracted_text = ""
        for element in del_elements:
            extracted_text += element.get_text()
        return extracted_text.strip()
    else:
        raise Exception(f"Response code: {response.status_code}")


class WebVisitor:
    def __init__(self, read_from_path: str, error_web_path: str = "./data/error_webs.csv"):
        self.logger = MyLogger(
            output_path="./data/log/web_visitor_logger.log", name="WebVisitor")
        self.read_from = read_from_path
        self.error_webs_path = error_web_path

    def get_title_and_url(self):
        with open(self.read_from, 'r', encoding="utf-8") as f:
            reader = csv.reader(f)  # csv format：[title, url]
            for row in reader:
                # "('Near Space Rocket-Powered Aircraft Beihang-4 Successfully Launched', 'https://ev.buaa.edu.cn/info/1097/2183.htm')"
                if len(row) == 0:
                    continue
                url = row[0]
                title = row[1] if len(row) == 2 else "".join(row[1:])
                yield title, url  # title, url

    def write_web_text_in_file(self, write_to_path: str = "./data/web_text.txt"):
        with open(write_to_path, 'a', encoding="utf-8") as f:
            article_cnt = 1
            for title, url in self.get_title_and_url():
                self.logger.info(f"Parsing web: {title},{url}")
                try:
                    web_text = get_web_text(url)
                    f.write(
                        f"ARTICLE_ID:{article_cnt}\nTITLE:{title}\nURL:{url}\nTEXT:\n{web_text}\n{SEPERATOR}"
                    )
                    article_cnt += 1
                except Exception as e:
                    error_data = [title, url]
                    with open(self.error_webs_path, "a", encoding="utf-8") as f_error:
                        csv.writer(f_error).writerow(error_data)
                    self.logger.warning(
                        f"Error occured when parsing web. {error_data}, {e}")
                    continue


if __name__ == '__main__':
    # todo Please replace the file name you want to filter.
    file_to_parse = [
        "./data/buaa_news.csv",
    ]
    for file in file_to_parse:
        WebVisitor(read_from_path=file).write_web_text_in_file()
