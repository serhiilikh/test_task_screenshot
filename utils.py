import re
import os.path
import contextlib

from pyvirtualdisplay import Display
from selenium import webdriver


def check_url_validity(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,'
        r'}\.?)|'  # domain... 
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


@contextlib.contextmanager
def selenium():
    display = Display(visible=True)
    display.start()
    path = os.path.join(os.getcwd(), "./chromedriver")
    browser = webdriver.Chrome(executable_path=path)
    try:
        yield browser
    finally:
        display.stop()
        browser.quit()
