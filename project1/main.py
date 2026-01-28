import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


chrome_options = webdriver.ChromeOptions() #크롬 브라우저 옵션 객체 생성
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), #크롬 버전에 맞는 드라이버 자동설치 후 크롬관연결
                          options=chrome_options) #이 옵션을 적용해서 크롬을 실행해라
사람인 = "https://www.saramin.co.kr/zf_user/"
잡코리아 = "https://www.jobkorea.co.kr/"

driver.get(사람인)

searchWord = '개발자'

searchReady = driver.find_element(By.CSS_SELECTOR, '#btn_search') #문서 전체에서 아무태그나 아이디 btn_search인거
searchReady.click()

input_box = driver.find_element(By.CSS_SELECTOR, "#ipt_keyword_recruit")
input_box.send_keys(searchWord)
time.sleep(2)
input_box.send_keys(Keys.ENTER)
time.sleep(2)


ppp = []
infos = driver.find_elements(By.CLASS_NAME,'item_recruit')

for info in infos:
    title = info.find_element(By.CLASS_NAME, 'job_tit')
    title = title.find_element(By.TAG_NAME, 'a').get_attribute('title')

    company = info.find_element(By.CLASS_NAME,'corp_name')
    company = company.find_element(By.TAG_NAME,'a').text
    due = info.find_element(By.CLASS_NAME,'job_date').text

    link = info.find_element(By.CLASS_NAME, 'job_tit')
    link = link.find_element(By.TAG_NAME, 'a').get_attribute('href')
    loc = info.find_element(By.CLASS_NAME, 'job_condition')
    loc = loc.find_elements(By.TAG_NAME, 'span')[0].text

    conditions = info.find_element(By.CLASS_NAME, 'job_condition')
    conditions = conditions.find_elements(By.TAG_NAME, 'span')[1:]
    temp = ""
    for i in conditions:
        temp = temp+" "+i.text
    ppp.append([title, company, due, link, loc, temp])


time.sleep(1)
df = pd.DataFrame(
    ppp,
    columns=["title", "company", "due", "link", "loc", "requirements"]
)

df.to_csv("첫페이지.csv", index=False,encoding='utf-8-sig')


