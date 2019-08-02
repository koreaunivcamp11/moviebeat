#!/usr/bin/env python
# coding: utf-8


# In[72]:


# 수민쓰 import
import sys
sys.path.append('..')
import crawling #이건 개취
from crawling import *
import math
import re
import numpy as np
from pprint import pprint
from bs4 import BeautifulSoup
# In[70]:


def get_decorator(errors=(Exception, ), default_value=''):

    def decorator(func):

        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors:
                print ("Got error! ")
                return default_value

        return new_func

    return decorator

nullerror = get_decorator((KeyError, TypeError), default_value='')
nullerror2 = get_decorator((KeyError, TypeError), default_value=['',''])



def crawNaverMVScore(dom):
    """ 네이버 영화에서 한 영화의 관람객, 평론가, 네티즌 평점을 가져오는 함수
    """
    try:
        score_aui = float([("".join(re.findall('([\d.])',_.text))) for _ in dom.select('#actualPointPersentBasic > .star_score > .st_off > .st_on')][0])
    except:
        score_aui = ''
        
    try:
        score_cri = round(float([_["style"].split(':')[1].split('%')[0]              for _ in dom.select('div.spc_score_area > .spc > .star_score > .st_off > .st_on')][0]) / 10,2)
    except:
        score_cri = ''
    try:
        score_net = round(float([_["style"].split(':')[1].split('%')[0] for _ in dom.select('#pointNetizenPersentBasic .st_off > .st_on')][0]) / 10,2 )
    except:
        score_net = ''
        
    return score_aui, score_cri, score_net
        

@nullerror    
def crawNaverMVtitle_kor(dom):
    """ 네이버 영화에서 한 영화의 한글 title 가져오는 함수
    """

    title_kor = [dom.select_one('div.mv_info_area > div.mv_info > h3.h_movie > a').text]
    return title_kor

@nullerror 
def crawNaverMVtitle_eng(dom):
    """ 네이버 영화에서 한 영화의 영어 title 가져오는 함수
    """
    title_forei = [_.text.replace("\r","").replace("\n","").replace("\t","").split(',') for _ in dom.select('.h_movie > .h_movie2')]
    title_eng = np.array(title_forei).flatten()
    if len(title_eng) > 2:
        title_eng = title_eng [:-1]
        return title_eng
    else:
        title_eng = title_eng [0]
        return title_eng

@nullerror 
def crawNaverMVgenre(dom):
    """ 네이버 영화에서 한 영화의 장르를 가져오는 함수
    """
    genre = [_.text.replace('\t','').replace('\r','').replace('\n','') for _ in dom.select('dl.info_spec > dd > p > span')][0]
    return genre


@nullerror 
def crawNaverMVcountry(dom):
    """ 네이버 영화에서 한 영화의 제작국가를 가져오는 함수
    """
    country = [_.text.replace('\t','').replace('\r','').replace('\n','') for _ in dom.select('dl.info_spec > dd > p > span')][1]
    return country


@nullerror 
def crawNaverMVruntime(dom):
    """ 네이버 영화에서 한 영화의 상영시간을 가져오는 함수
    """
    runtime = [_.text.replace('\t','').replace('\r','').replace('\n','') for _ in dom.select('dl.info_spec > dd > p > span')][2]        
    return runtime


@nullerror 
def crawNaverMVopendate(dom):
    """ 네이버 영화에서 한 영화의 개봉일을 가져오는 함수
    """
    opendate = [_.text.replace('\t','').replace('\r','').replace('\n','').replace(" ","").replace("개봉","") for _ in dom.select('dl.info_spec > dd > p > span')][3].split(',')[-1]
    return opendate


@nullerror 
def crawNaverMVfilm_rate(dom):
    """ 네이버 영화에서 한 영화의 관람등급을 가져오는 함수
    """
    film_rate = [_.text.replace('\t','').replace('\r','').replace('\n','').split('도')[0] for _ in dom.select('dl.info_spec > dt.step4 ~ dd > p')]        
    return film_rate


@nullerror 
def crawNaverMVpublic(dom):
    """ 네이버 영화에서 한 영화의 홍보문구를 가져오는 함수
    """
    public = [_.text for _ in dom.select('.obj_section > .video > .story_area > h5')]
    return public


@nullerror 
def crawNaverMVsummary(dom):
    """ 네이버 영화에서 한 영화의 줄거리를 가져오는 함수
    """
    summary = [_.text for _ in dom.select('.obj_section > .video > .story_area > p')]
    return summary


@nullerror 
def crawNaverMVstaff_img(dom):            # 배우사진 감독사진 나눠야할까 ? (이름이랑 역할은 다 나눴음)
    """ 네이버 영화에서 한 영화의 staff들의 사진을 가져오는 함수
    """
    staff_img = [_["src"] for _ in dom.select('.obj_section > .people > ul > li > a > img')]
    return staff_img


@nullerror 
def crawNaverMVstaff_prod(dom):
    """ 네이버 영화에서 한 영화의 감독 이름을 가져오는 함수
    """
    staff_prod = [_["title"] for _ in dom.select('.obj_section > .people a.tx_people')][0]
    return staff_prod


@nullerror 
def crawNaverMVstaff_act(dom):
    """ 네이버 영화에서 한 영화의 배우들 이름을 가져오는 함수
    """
    staff_act = [_["title"] for _ in dom.select('.obj_section > .people a.tx_people')][1:]
    return staff_act


@nullerror 
def crawNaverMVact_role(dom):
    """ 네이버 영화에서 한 영화의 배우별 역할이름을 가져오는 함수 
    """
    act_role = [_.text.split('\n')[2] for _ in dom.select('.obj_section > .people .staff')][1:]
    return act_role


@nullerror 
def crawNaverMVreco_title(dom):      
    """ 네이버 영화에서 한 영화의 추천영화 이름들을 가져오는 함수 
    """
    reco_title = [_.text for _ in dom.select('ul.thumb_link_mv > li > a.title_mv')]
    return reco_title


@nullerror 
def crawNaverMVreco_url(dom):
    """ 네이버 영화에서 한 영화의 배우별 역할이름을 가져오는 함수 
    """
    reco_url = [requests.compat.urljoin("https://movie.naver.com", _["href"]) for _ in dom.select('ul.thumb_link_mv > li > a.title_mv')]
    return reco_url      

@nullerror2 
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
        
    return quote_seed, url

@nullerror2 
def getQuotes(pagelist, movie_url):
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
    driver.get(movie_url) #다 긁었으면 영화소개 페이지로 다시 돌아가라
    return famous_lines, role, actor



def quotesfromNaver(url):
    """네이버 영화 url을 넣으면 famous_lines, role, actor 리스트 가져오는 함수
        우리의 url은 전부 tuple 형식임을 잊지 맙시다
    """
    quotepageList, movie_url = createQuoteList(url)
    #print(quotepageList)
    famous_lines, role, actor = getQuotes(quotepageList, movie_url)
    return famous_lines, role, actor



def crawNaverMVInfo(url):               
    """ 네이버 영화의 한 영화 페이지에 들어가서 내용 다 가져오는 함수
    """
    html = download("get", url)
    dom = BeautifulSoup(html.text, "lxml")

    famous_lines, role, actor = quotesfromNaver(url)
    return {("score_aui", "score_cri", "score_net") : crawNaverMVScore(dom), 
            "title_kor" : crawNaverMVtitle_kor(dom), 
            "title_eng" : crawNaverMVtitle_eng(dom), 
            "genre" : crawNaverMVgenre(dom), 
            "country" : crawNaverMVcountry(dom), 
            "runtime" : crawNaverMVruntime(dom), 
            "opendate" : crawNaverMVopendate(dom), 
            "film_rate" : crawNaverMVfilm_rate(dom),
            "public" : crawNaverMVpublic(dom), 
            "summary" : crawNaverMVsummary(dom), 
            "staff_img" : crawNaverMVstaff_img(dom), 
            "staff_prod" : crawNaverMVstaff_prod(dom), 
            "staff_act" : crawNaverMVstaff_act(dom), 
            "act_role" : crawNaverMVact_role(dom), 
            "reco_title" : crawNaverMVreco_title(dom) , 
            "reco_url" : crawNaverMVreco_url(dom) , 
            "famous_lines" : famous_lines, 
            "role" : role, 
            "actor" : actor 
           }


# In[74]:


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
    #print(baseURL)
    seen.append(baseURL)
    time.sleep(1)
        
    movieinfo=crawNaverMVInfo(baseURL)
    recoList = movieinfo["reco_url"] ##
    pprint(movieinfo)
    title_list_kor.append(movieinfo["title_kor"])
    for link in recoList:
        if link not in queue and link not in seen and not None:
            queue.append(link)
    print("queue: {0}, seen:{1}".format(len(queue),len(seen)))
    #queue.extend(linkList)


# In[73]:


driver.close()


# In[ ]:



# def createQuoteList(url):
#     """네이버 영화 페이지를 입력하면 총 명대사 페이지로 이동한 뒤에 총 명대사 페이지 url 리스트로 가져오기
#     """
#     driver.get(url)
#     driver.find_element_by_css_selector(".best_lines a").click()  # 명대사 페이지로 이동
#     driver.switch_to.frame("scriptIframe") 
#     tot_quote_num = int(driver.find_element_by_css_selector('#iframeDiv > div > span.cnt >em').text) #전체 명대수 개수
#     quote_page_num = math.ceil(tot_quote_num/10) #명대사 페이지 개수
#     quote_page = driver.find_element_by_css_selector('div.paging > div > a').get_attribute("href")
#     page_base = ''.join(re.split("(&page=)(\d+)", quote_page)[:2])
#     quote_seed = list()
#     for _ in range(quote_page_num):
#         quote_seed.append(page_base+str(_+1))
        
#     return quote_seed


# def getQuotes(pagelist):
#     """명대사 페이지 url 리스트 넣으면 명대사, 등장인물 이름, 배우이름 리스트 가져오는 함수
#     """
#     famous_lines =[]
#     role = []
#     actor = []
#     for quotepageURL in pagelist:
#         driver.execute_script("javascript:window.open('about:blank');") #새로운 창을 열고
#         driver.switch_to_window(driver.window_handles[-1]) #driver를 여기로 switch해주고
#         driver.get(quotepageURL)
#         best_lines = [_.text for _ in driver.find_elements_by_css_selector(' #iframeDiv > ul.lines > li > div > p.one_line, p.char_part > span, p.char_part > a')]
#         for x,y in enumerate(best_lines):
#             if x%3==0:
#                 famous_lines.append(y)
#             if x%3==1:
#                 role.append(y.replace("목소리", ""))
#             if x%3==2:
#                 actor.append(y)
#         driver.close() #다 읽은 창을 닫고
#         driver.switch_to_window(driver.window_handles[-1]) #driver를 원래 창으로
#     return famous_lines, role, actor

