#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
sys.path.append('..')
import crawling #이건 개취
from crawling import *
import math
import re


def createQuoteList(url):
    """네이버 영화 페이지를 입력하면 총 명대사 페이지로 이동한 뒤에 총 명대사 페이지 url 리스트로 가져오기
    """
    driver.get(url)
    driver.find_element_by_css_selector(".best_lines a").click()  # 명대사 페이지로 이동
    driver.switch_to.frame("scriptIframe") 
    tot_quote_num = int(driver.find_element_by_css_selector('#iframeDiv > div > span.cnt >em').text) #전체 명대수 개수
    quote_page_num = math.ceil(tot_quote_num/10) #명대사 페이지 개수
    quote_page = driver.find_element_by_css_selector('div.paging > div > a').get_attribute("href")
    page_base = ''.join(re.split("(&page=)(\d+)", quote_page)[:2])
    quote_seed = list()
    for _ in range(quote_page_num):
        quote_seed.append(page_base+str(_+1))
        
    return quote_seed


def getQuotes(pagelist):
    """명대사 페이지 url 리스트 넣으면 명대사, 등장인물 이름, 배우이름 리스트 가져오는 함수
    """
    famous_lines =[]
    role = []
    actor = []
    for quotepageURL in pagelist:
        driver.execute_script("javascript:window.open('about:blank');") #새로운 창을 열고
        driver.switch_to_window(driver.window_handles[-1]) #driver를 여기로 switch해주고
        driver.get(quotepageURL)
        best_lines = [_.text for _ in driver.find_elements_by_css_selector(' #iframeDiv > ul.lines > li > div > p.one_line, p.char_part > span, p.char_part > a')]
        for x,y in enumerate(best_lines):
            if x%3==0:
                famous_lines.append(y)
            if x%3==1:
                role.append(y.replace("목소리", ""))
            if x%3==2:
                actor.append(y)
        driver.close() #다 읽은 창을 닫고
        driver.switch_to_window(driver.window_handles[-1]) #driver를 원래 창으로
    return famous_lines, role, actor


def quotesfromNaver(url):
    """네이버 영화 url을 넣으면 famous_lines, role, actor 리스트 가져오는 함수
    """
    quotepageList = createQuoteList(url[0])
    #print(quotepageList)
    famous_lines, role, actor = getQuotes(quotepageList)
    return famous_lines, role, actor



import requests
import time
from pprint import pprint
#from download import download
from bs4 import BeautifulSoup
from functools import reduce



def crawNaverMVRank(seed):
    """ 네이버 영화에서 관람객, 평론가, 네티즌 평점을 가져오는 함수
    """
   
    try:
        rank_aui = float([("".join(re.findall('([\d.])',_.text))) for _ in dom.select('#actualPointPersentBasic > .star_score > .st_off > .st_on')][0])
    except:
        rank_aui = ''
        
    try:
        rank_cri = round(float([_["style"].split(':')[1].split('%')[0]              for _ in dom.select('div.spc_score_area > .spc > .star_score > .st_off > .st_on')][0]) / 10,2)
    except:
        rank_cri = ''
    try:
        rank_net = round(float([_["style"].split(':')[1].split('%')[0] for _ in dom.select('#pointNetizenPersentBasic .st_off > .st_on')][0]) / 10,2 )
    except:
        rank_net = ''
        
    return rank_aui, rank_cri, rank_net



def parseContent(seed):    
    """ 한 영화 페이지에 들어가서 해당 페이지 기본 내용 다 긁어오기, 
    함수 단위로 더 쪼개서 수정될 예정(crawNaverMVRank)
    best_lines 삭제, title_reco (추천 영화 제목 5개), url_reco (추천 영화 링크 5개, 이걸 타고 들어가야 합니다)
    """
    html = download("get", seed)
    dom = BeautifulSoup(html.text, "lxml")
    
    rank_aui, rank_cri, rank_net = crawNaverMVRank(seed)
    
    return {"title_kor":[dom.select_one('div.mv_info_area > div.mv_info > h3.h_movie > a').text],
            "title_eng":[_.text.split('\r')[0] for _ in dom.select('.h_movie > .h_movie2')],
            "rank_aui":rank_aui,
             "rank_cri":rank_cri,
            "rank_net": rank_net,
            ("genre","country","runtime","opendate"):[_.text.strip() for _ in dom.select('dl.info_spec > dd > p > span')],
            "film_rate":[_.text for _ in dom.select('dl.info_spec > dd > p > a')][-3:-1],
            "public":[_.text.strip() for _ in dom.select('.obj_section > .video > .story_area > h5')],
            "summary":[_.text.strip() for _ in dom.select('.obj_section > .video > .story_area > p')],
            "prod_role":[_.text.split('\n')[2] for _ in dom.select('.obj_section > .people .staff')][1:],
            "prod_prod":[_["title"] for _ in dom.select('.obj_section > .people a.tx_people')][0],
            "prod_actor":[_["title"] for _ in dom.select('.obj_section > .people a.tx_people')][1:],
            "prod_img":[_["src"] for _ in dom.select('.obj_section > .people > ul > li > a > img')],
            "title_reco" : [_.text for _ in dom.select('ul.thumb_link_mv > li > a.title_mv')],
            "url_reco" : [requests.compat.urljoin("https://movie.naver.com", _["href"]) for _ in dom.select('ul.thumb_link_mv > li > a.title_mv')]
            # , "best_lines":[_.text for _ in dom.select('#iframeDiv > ul.lines > li > div > p.one_line')]
           }




from selenium import webdriver
driver = webdriver.Chrome()

url = "https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=pnt&date=20190729"
html = download("get", url)
dom = BeautifulSoup(html.text, "lxml")

seed = list()
seed.extend([requests.compat.urljoin(url, _["href"]) for _ in dom.select("td.title > div.tit5 > a")])
# seed에 평점순 50개 영화 url 넣음

queue =list()
queue.extend(seed)
#print(queue)

seen=list()
title_list_kor = []
while queue:
    baseURL=queue.pop(0)
    seen.append(baseURL)
    time.sleep(1)
        
    linkList=parseContent(baseURL) #지원쓰 우리 영화정보 받아오는 리스트의 이름을 linkList에서 다른 것으로 바꿉시다
    famous_lines, role, actor = quotesfromNaver(baseURL)
    recoList = linkList["url_reco"] ##
    pprint(linkList)
    title_list_kor.append(linkList["title_kor"])
    for link in recoList:
        if link not in queue and link not in seen:
            queue.append(link)
    print("queue: {0}, seen:{1}".format(len(queue),len(seen)))


    
    
    
#print(title_list_kor)

