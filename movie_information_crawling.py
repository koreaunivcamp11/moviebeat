#!/usr/bin/env python
# coding: utf-8

# In[2]:


import sys
import requests
import time
from pprint import pprint
from bs4 import BeautifulSoup
import re
import math
import numpy as np
import pickle


# In[4]:


def download(method, url, headers=None, param=None, data=None, timeout=1, maxretries=3):
    """ 해당 url에 http 요청을 보내서 html을 받는 함수
    """
    
    try: 
        resp = requests.request(method, url, params=param, data=data, headers = headers)         
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if 500 <= e.response.status_code < 600         and maxretries > 0:
            print(maxretries)
            time.sleep(timeout)
            resp = download(method,url,param,data,timeout,maxretries-1)  
        else:
            print(e.response.status_code)
            print(e.response.reason)
    return resp


# In[5]:


def get_decorator(errors=(Exception, ), default_value=None):
    """ error가 나면 None 값을 넣고 넘어가는 함수
    """

    def decorator(func):

        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                print ("Got error! ")
                return default_value

        return new_func

    return decorator

nullerror = get_decorator((KeyError, TypeError), default_value=None) #error가 난다면 null을 넣고 넘어갑시다
nullerror2 = get_decorator((KeyError, TypeError), default_value=['','']) #값을 2개 받아와야 하면 null 2개 넣어버리지요


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
        


# In[6]:


@nullerror    
def crawNaverMVtitle_kor(dom):
    """ 네이버 영화에서 한 영화의 한글 title 가져오는 함수
    """

    title_kor = dom.select_one('div.mv_info_area > div.mv_info > h3.h_movie > a').text
    return title_kor

@nullerror 
def crawNaverMVtitle_eng(dom):
    """ 네이버 영화에서 한 영화의 영어 title 가져오는 함수
    """
    title_forei =  dom.select_one('div.mv_info_area > div.mv_info > .h_movie2').text
    
    title_eng = np.array(title_forei).flatten()
    if len(title_eng) > 2:
        title_eng = str(title_eng [:-1])
        return title_eng
    else:
        title_eng = title_eng [0]
        return title_eng


# In[7]:


@nullerror
def crawNaverMVposter(dom):
    """ 네이버 영화에서 한 영화의 포스터를 가져오는 함수
    """
    poster = dom.select_one('.poster img')["src"]
    return poster

@nullerror 
def crawNaverMVgenre(dom):
    """ 네이버 영화에서 한 영화의 장르를 가져오는 함수
    """
    genre = [_.text.replace('\t','').replace('\r','').replace('\n','') for _ in dom.select('dl.info_spec > dd > p > span')][0]
    return genre


@nullerror 
def crawNaverMVcountry(dom):
    """ 네이버 영화에서 한 영화의 제작 국가를 가져오는 함수
    """
    country = [_.text.replace('\t','').replace('\r','').replace('\n','') for _ in dom.select('dl.info_spec > dd > p > span')][1]
    return country


@nullerror 
def crawNaverMVruntime(dom):
    """ 네이버 영화에서 한 영화의 상영 시간을 가져오는 함수
    """
    runtime = [_.text.replace('\t','').replace('\r','').replace('\n','') for _ in dom.select('dl.info_spec > dd > p > span')][2]        
    return runtime


@nullerror 
def crawNaverMVopendate(dom):
    """ 네이버 영화에서 한 영화의 개봉 일자를 가져오는 함수
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
def crawNaverMVsummary(dom):
    """ 네이버 영화에서 한 영화의 요약본을 가져오는 함수
    """

    summary = dom.select_one('.obj_section > .video > .story_area > h5').text
    return summary


@nullerror 
def crawNaverMVstory(dom):
    """ 네이버 영화에서 한 영화의 줄거리를 가져오는 함수
    """
    story = [_.text for _ in dom.select('.obj_section > .video > .story_area > p')]
    return story


@nullerror 
def crawNaverMVprod_img(dom):         
    """ 네이버 영화에서 한 영화의 staff들의 사진을 가져오는 함수
    """
    prod_img = [_["src"] for _ in dom.select('.obj_section > .people > ul > li > a > img')][0]
    return prod_img

@nullerror 
def crawNaverMVact_img(dom):            
    """ 네이버 영화에서 한 영화의 staff들의 사진을 가져오는 함수
    """
    act_img = [_["src"] for _ in dom.select('.obj_section > .people > ul > li > a > img')][1:]
    return act_img


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


# In[8]:


@nullerror2 
def createQuoteList(url):
    """네이버 영화 페이지를 입력하면 총 명대사 페이지로 이동한 뒤에 총 명대사 페이지 url 리스트로 가져오기
    """
    html = download("get", url)
    dom = BeautifulSoup(html.text, "lxml") 
    
    page_base = requests.compat.urljoin(url,dom.select_one('.best_lines > .title_area.type_btn_box > a')["href"])
    
    html = download("get", page_base)
    dom = BeautifulSoup(html.text, "lxml") 

    quotes_page = requests.compat.urljoin(page_base, dom.select_one('#scriptIframe')["src"])
    html = download("get", quotes_page)
    dom = BeautifulSoup(html.text, "lxml") 

    tot_quotes_num = int(dom.select_one('#iframeDiv > div > span.cnt >em').text) #전체 명대수 개수
    quotes_page_num = math.ceil(tot_quotes_num/10) #명대사 페이지 개수
    
    quote_seed = list()

    for _ in range(1,quotes_page_num+1):
        quote_seed.append(quotes_page+"&page="+str(_))

    return quote_seed


# In[9]:



@nullerror2 
def getQuotes(pagelist):
    """명대사 페이지 url 리스트 넣으면 명대사, 등장인물 이름, 배우이름 리스트 가져오는 함수
    """    
    quote =[]
    role = []
    actor = []
    for quotepageURL in pagelist:
            html = download("get", quotepageURL)
            dom = BeautifulSoup(html.text, "lxml") 
            for line_area2 in dom.select('.lines_area2'):
                
                quote.append(line_area2.select_one(".one_line").text)
                
                try:
                    role.append(line_area2.select_one(".char_part > span").text)
                except:
                    role.append(None)
                try:
                    actor.append(line_area2.select_one(".char_part > a").text)
                except:
                    actor.append(None)  

    len_quotes = len(quote)
    return quote, role, actor, len_quotes
    
    
def quotesfromNaver(url):
    """네이버 영화 url을 넣으면 quote, role, actor 리스트와 len_quotes 가져오는 함수
        우리의 url은 전부 tuple 형식임을 잊지 맙시다
    """
    quotepageList = createQuoteList(url)
    quote, role, actor, len_quotes = getQuotes(quotepageList)
    return quote, role, actor, len_quotes


def crawNaverMVInfo(url):              
    """ 네이버 영화의 한 영화 페이지에 들어가서 내용 다 가져오는 함수
    """
    
    html = download("get", url)
    dom = BeautifulSoup(html.text, "lxml") 
    
    quote, role, actor, len_quotes = quotesfromNaver(url)
    return {("score_aui", "score_cri", "score_net") : crawNaverMVScore(dom), 
            "title_kor" : crawNaverMVtitle_kor(dom), 
            "title_eng" : crawNaverMVtitle_eng(dom), 
            "poster" : crawNaverMVposter(dom),
            "genre" : crawNaverMVgenre(dom), 
            "country" : crawNaverMVcountry(dom), 
            "runtime" : crawNaverMVruntime(dom), 
            "opendate" : crawNaverMVopendate(dom), 
            "film_rate" : crawNaverMVfilm_rate(dom),
            "summary" : crawNaverMVsummary(dom), 
            "story" : crawNaverMVstory(dom), 
            "prod_img" : crawNaverMVprod_img(dom), 
            "act_img" : crawNaverMVact_img(dom), 
            "staff_prod" : crawNaverMVstaff_prod(dom), 
            "staff_act" : crawNaverMVstaff_act(dom), 
            "act_role" : crawNaverMVact_role(dom), 
            "reco_title" : crawNaverMVreco_title(dom) , 
            "reco_url" : crawNaverMVreco_url(dom) , 
            "quote" : quote, 
            "actor" : actor, 
            "role" : role, 
            "len_quotes" : len_quotes
           }


# In[ ]:


import sqlite3
con = sqlite3.connect("real_crawling_ver2.db")
cur = con.cursor()

cur.executescript(
            """
            CREATE TABLE NVmovie(
            id     INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            title_kor TEXT NOT NULL,        
            title_eng TEXT NOT NULL,
            score_aui REAL,
            score_cri REAL,
            score_net REAL,
            poster TEXT,
            genre TEXT,
            country TEXT,
            runtime TEXT,
            opendate TEXT,
            film_rate TEXT,
            summary TEXT,
            story TEXT,
            prod_img TEXT,
            staff_prod TEXT,
            len_quotes INTEGER 
            );     
            
            CREATE TABLE NVactor(
            id     INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            movie_key INTEGER NOT NULL,
            act_img TEXT,
            staff_act TEXT,
            act_role TEXT
            );   
            
            CREATE TABLE NVreco_movie(
            id     INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            movie_key INTEGER NOT NULL,
            reco_title TEXT, 
            reco_url TEXT 
            );
                 
            CREATE TABLE NVquotes(
            id     INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            movie_key INTEGER NOT NULL,
            quote TEXT, 
            actor TEXT,
            role TEXT,
            real_quote TEXT,
            isreal INTEGER NOT NULL
            );          
            """
)
con.commit()

queue =list()
seen=list()
title_list_kor = []
weird_queue = list()
id=1

url_zero = "https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=pnt&date=20190729"

for page_number in range(1,5):
    page_param = "&page="+str(page_number)

    url = url_zero + page_param

    html = download("get", url)
    dom = BeautifulSoup(html.text, "lxml")

    queue.extend([requests.compat.urljoin(url, _["href"]) for _ in dom.select("td.title > div.tit5 > a")])
    
while queue:
    baseURL = queue.pop(0)
    seen.append(baseURL)
    time.sleep(1)

    try:    
        movieinfo=crawNaverMVInfo(baseURL)

        pprint(movieinfo)

        cur.execute("INSERT INTO NVmovie(title_kor,title_eng,score_aui,score_cri,score_net,poster,        genre,country,runtime,opendate,film_rate,summary,story,prod_img,staff_prod,len_quotes)        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [ movieinfo["title_kor"], movieinfo["title_eng"], 
        movieinfo[("score_aui", "score_cri", "score_net")][0], movieinfo[("score_aui", "score_cri", "score_net")][1], 
        movieinfo[("score_aui", "score_cri", "score_net")][2], movieinfo["poster"], movieinfo["genre"],
        movieinfo["country"], movieinfo["runtime"], movieinfo["opendate"], movieinfo["film_rate"][0], 
        movieinfo["summary"], movieinfo["story"][0],movieinfo["prod_img"],movieinfo["staff_prod"], movieinfo["len_quotes"]]
                   )

        num = len(movieinfo["staff_act"])
        for i in range(num):
            cur.execute("INSERT INTO NVactor(movie_key, act_img, staff_act, act_role)            VALUES(?,?,?,?)",[id, movieinfo["act_img"][i],movieinfo["staff_act"][i], movieinfo["act_role"][i]])

        reco_num = len(movieinfo["reco_title"])
        for i in range(reco_num):
            cur.execute("INSERT INTO NVreco_movie(movie_key, reco_title, reco_url)            VALUES(?,?,?)",[id, movieinfo["reco_title"][i],movieinfo["reco_url"][i]])

        for i in range(movieinfo["len_quotes"]):
            cur.execute("INSERT INTO NVquotes(movie_key, quote, actor, role, isreal)            VALUES(?,?,?,?,?)",[id, movieinfo["quote"][i],movieinfo["actor"][i],movieinfo["role"][i],0])

        recoList = movieinfo["reco_url"] 
        title_list_kor.append(movieinfo["title_kor"])
        for link in recoList:
            if link not in queue and link not in seen and not None:
                queue.append(link)

        con.commit()
        id+=1

    except:
        con.rollback()
        weird_queue.append(baseURL) 


# In[ ]:




