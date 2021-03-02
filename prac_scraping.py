from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
import requests


client = MongoClient("내AWS아이피", 27017, username="아이디", password="비밀번호")
db = client.dbsparta_plus_week3

driver = webdriver.Chrome("./chromedriver")

url = "http://matstar.sbs.co.kr/location.html"

driver.get(url)
time.sleep(5)

req = driver.page_source
driver.quit()

soup = BeautifulSoup(req, "html.parser")

places = soup.select("ul.restaurant_list > div > div > li > div > a")
print(len(places))
