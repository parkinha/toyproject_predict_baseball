import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup

import pandas as pd
import numpy as np

import re


print("1팀 라인업을 타자, 투수 순으로 입력해주세요")
#b1,b2,b3,b4,b5,b6,b7,b8,b9,pitcher1=input().split()
print("2팀 라인업을 타자, 투수 순으로 입력해주세요")
#a1,a2,a3,a4,a5,a6,a7,a8,a9,pitcher2=input().split()
#print(b1,b2,b3,b4,b5,pitcher)

#크롬드라이버로 연결 path를 내걸로 수정해야함
driver = webdriver.Chrome(executable_path = "C:/Users/Administrator/Downloads/chromedriver_win32/chromedriver.exe") #"C:/Users/희준/downloads/chromedriver_win32/chromedriver.exe")


#YS=시즌시작년도 YE=시즌종료년도SN=한페이지에 몇명선수 불러올지 pa=몇번째선수부터 불러올지
for i in range(4):  
    #롯데 타자들 있는 url로 바꿔줄것
    url = 'http://www.statiz.co.kr/stat.php?mid=stat&re=0&ys=2022&ye=2022&sn=100&pa={}'.format(i*100)
    driver.get(url)
    #설정시간동안 로딩되지않으면 에러가 발생함
    driver.implicitly_wait(time_to_wait=5)
    #find_element(By.XPATH)는 xpath 경로를 사용하여 원하는 element를 가져오는 함수이다. 원하는 선수들의 성적이 적힌 테이블은 mytable이란 아이디에 기록이 되어있다. 그 중에서도 tbody라는 요소에 표 형식으로 기록이 되어있다. 즉, 선수들의 정보가 담긴 tbody란 표를 통째로 가져온다
    html = driver.find_element(By.XPATH,'//*[@id="mytable"]/tbody').get_attribute("innerHTML")
    #beautiful soup 객체에 넣어줌으로써 태그검색을 쉽게 만듬
    soup = BeautifulSoup(html, 'html.parser')
    
    temp = [i.text.strip() for i in soup.findAll("tr")] #tr태그에서 text만 저장하고 공백 제거
    temp = pd.Series(temp) #list 객체를 series 객체로 변경
    
    #중간중간에 '순'이나 'WAR'로 시작하는 행들이 있는데 이를 제거해준다
    #그리고 index를 reset
    temp = temp[~temp.str.match("[순W]")].reset_index(drop=True)
    
    #띄어쓰기 기준으로 분류해서 데이터프레임으로 만들기
    temp = temp.apply(lambda x: pd.Series(x.split(' ')))
    
    #선수 팀 정보 이후 첫번째 기록과는 space 하나로 구분, 그 이후로는 space 두개로 구분이 되어 있음 
    #그래서 space 하나로 구분을 시키면, 빈 column들이 존재 하는데, 해당 column들 제거 
    temp = temp.replace('', np.nan).dropna(axis=1) 
    
    #WAR이 두 열이나 존재해서 처음 나오는 WAR열을 삭제. 1열에 있음
    temp = temp.drop(1,axis=1)
    
    #선수 이름 앞의 숫자 제거
    temp[0] = temp[0].str.replace("^\d+", "")
    
    
    if i ==0:
        result = temp
    else:
        result = pd.concat([result,temp]) #result.append(temp)
        result = result.reset_index(drop=True)
    print(i, "완료")
    
columns = ['선수'] + [i.text for i in soup.findAll("tr")[0].findAll("th")][4:-3] + ['타율','출루율','장타율','OPS','wOBA','wRC+','WAR+','WPA']
result.columns = columns
print('a')
driver.close()

#선수 이름을 슬라이싱하여 새로운 열로 추가
result['이름'] = result['선수'].map(lambda x:x[:x.find('22')])
#선수 포지션을 슬라이싱하여 새로운 열로 추가
result['포지션'] = result['선수'].map(lambda x:x[x.find('22')+3:])
print('b')
# 투수교체나 대타 기용 과정에서 타석에 들어선 것으로 처리되는 투수들이 간혹 있음
# 이 투수들의 row를 삭제해주기 위한 과정
pitcher_index = result[result['포지션']=='P'].index
result.drop(pitcher_index, inplace=True)
print(result)
result.to_excel('baseball.xlsx')
