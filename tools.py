import csv
import logging
import os
import pickle
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class MyLogger:
    def __init__(self, name, output_path=None, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        output_path = output_path if output_path else f".data/log/{name}.log"
        if not os.path.exists(output_path):
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as fp:
                fp.write("")

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler(output_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        # console的level是info，存取文件的level是debug
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


def save_as_csv(data, file_path):
    # csv格式：[title, url]
    with open(file_path, "a", encoding="utf-8") as output_result_file:
        writer = csv.writer(output_result_file)
        # 拆分元组
        for title, url in data:
            writer.writerow([url, title])


def init_firefox_driver():
    options = FirefoxOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--incognito")
    options.add_argument(f"--user-data-dir=./temp")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-save-password-bubble")
    return webdriver.Firefox(options=options)


def init_chrome_driver():
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(chrome_options=chrome_options)


def get_random_user_agent(ua_list):
    return random.choice(ua_list)


def get_random_domain():
    domain_list = get_data("meta/all_domain.txt")
    BLACK_DOMAIN = ["www.google.gf", "www.google.io", "www.google.com.lc"]
    domain = random.choice(domain_list)
    if domain in BLACK_DOMAIN:
        get_random_domain()
    else:
        return domain


def get_data(file_path):
    """Read data from file and output data in list format

    Args:
        file_path ([str]): file path
    """
    text_list = []
    with open(file_path, encoding="utf-8") as fp:
        for line in fp:
            line = line.replace("\n", "").strip()
            if line:
                text_list.append(line)
    return text_list


def save_cookies(driver, cookies_file_path):
    with open(cookies_file_path, "wb") as f:  # pickle must use "wb" and "rb"
        pickle.dump(driver.get_cookies(), f)


def load_cookies(driver, cookies_file_path):
    if os.path.exists(cookies_file_path):
        with open(cookies_file_path, "rb") as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        return True
    return False


def manual_login(driver, cookies_file):
    input("Please loging and press Enter to continue...")
    save_cookies(driver, cookies_file)  # save cookies
    print("程序正在继续运行")


def get_firefox_driver(options=None):
    options = get_firefox_options() if None else options
    driver = webdriver.Firefox(options=options)
    return driver


def get_firefox_options(temp_dir="./temp"):
    options = FirefoxOptions()
    get_options(options, temp_dir)
    return options


def get_options(options, temp_dir="./temp"):
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--incognito")
    options.add_argument(f"--user-data-dir={temp_dir}")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-save-password-bubble")
    return options


def get_chrome_options(temp_dir="./temp"):
    chrome_options = ChromeOptions()
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-gpu")
