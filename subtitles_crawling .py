#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')
from bs4 import BeautifulSoup
import math
import re
import numpy as np
from random import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests
import time
import os
import shutil
import zipfile


# In[3]:


import pickle
with open("pickle_title_kor.txt", "rb") as f:
    real_title_list_KOR= pickle.load(f)


# In[4]:


with open("pickle_title_eng_list.txt", "rb") as f:
    real_title_list_ENG= pickle.load(f)


# In[11]:


real_title_list_ENG[:5]
real_title_list_ENG[8621]


# In[153]:


with open("zero_movie_key", "rb") as f:
    zero_movie_key = pickle.load(f)


# In[154]:


# 준비 : subtitle 폴더 안에 zip 폴더를 만들어 놓는다
filepath = os.path.abspath('C:\\Users\\gi427\\Downloads\\subtitle')
filepath_zip = os.path.abspath("C:\\Users\\gi427\\Downloads\\subtitle\\zip")
filename = max([filepath + "\\" + f for f in os.listdir(filepath)], key = os.path.getctime)

filename


# In[155]:


zero_movie_key


# In[156]:


real_title_list_KOR


# In[157]:


real_title_list_ENG


# In[168]:


headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
def download(method, url, param=None, data=None, timeout=1, maxretries=3):
    try:
        resp = requests.request(method, url, params=param, data=data, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if 500 <= e.response.status_code < 600         and maxretries > 0:
            print(maxretries)
            time.sleep(timeout)
            resp = download(method, url, param, data, timeout, maxretries-1)
            #print("재시도")
        else:
            print(e.response.status_code)
            print(e.response.reason)
    return resp


# In[169]:


def filename(mov,index):
    time.sleep(2)
    index = index + 1
    
    filepath = os.path.abspath('C:\\Users\\gi427\\Downloads\\subtitle')
    filepath_zip = os.path.abspath("C:\\Users\\gi427\\Downloads\\subtitle\\zip")
    
    filename = max([filepath + "\\" + f for f in os.listdir(filepath)], key = os.path.getctime)
    if(filename.split('.')[-1]=="zip"): 
        '''만약 zip file 일경우,
            1. index+영화이름 인 폴더를만듬.
            2. zip 폴더안의 새로운 폴더에 압축을품.
            3. 해당 알집파일을 index + 파일 로 이름 바꾼뒤 zip 폴더에 , 저장함.
        '''
        os.mkdir(filepath_zip+"\\"+str(index)+" "+mov)
        with zipfile.ZipFile(filename,"r") as zip_ref:
            zip_ref.extractall(filepath_zip+"\\"+str(index)+" "+mov)
        shutil.move(os.path.join(filepath_zip,filename),filepath_zip+"\\"+str(index)+" "+(filename.split('.')[-1])+" "+mov+".zip")
    elif(filename.split('.')[-1]=="rar"):
        os.mkdir(filepath_zip+"\\"+str(index)+" "+mov)
        with zipfile.ZipFile(filename,"r") as zip_ref:
            zip_ref.extractall(filepath_zip+"\\"+str(index)+" "+mov)
        shutil.move(os.path.join(filepath_zip,filename),filepath_zip+"\\"+str(index)+" "+(filename.split('.')[-1])+" "+mov+".rar")
    elif(filename.split('.')[-1]=="egg"):
        os.mkdir(filepath_zip+"\\"+str(index)+" "+mov)
        with zipfile.ZipFile(filename,"r") as zip_ref:
            zip_ref.extractall(filepath_zip+"\\"+str(index)+" "+mov)
        shutil.move(os.path.join(filepath_zip,filename),filepath_zip+"\\"+str(index)+" "+(filename.split('.')[-1])+" "+mov+".egg")
    else:
        shutil.move(os.path.join(filepath,filename),filepath+"\\"+str(index)+" "+(filename.split('.')[-1])+" "+mov+".txt")            


# In[170]:


def checkCineBoard(url):    
    """ 씨네스트 자막 게시판의 제목 가져오기
    """
    html = download("get", url) 
    dom = BeautifulSoup(html.text, "lxml")
    title = dom.select_one('script ~ h1').text.strip()
    return title


# In[171]:


def english_title_match(mv, eng_title):
    """영어 단어 개수를 비교해서 True / False 리턴하는 함수"""
    eng = re.compile('[A-Za-z]+') #영어 단어 개수를 비교해서 그래도 최소한의 단어가 겹치면 맞는 것으로 간주
    mv_set = set(eng.findall(mv))
    eng_title_set = set(eng.findall(eng_title))
    if len(set(mv_set) & set(eng_title_set)) >= min(len(mv_set),len(eng_title_set)):
        return True
    else:
        return False


# In[172]:


def korean_title_match(mv, kor_title):
    """한국어 단어 개수를 비교해서 True / False 리턴하는 함수"""
    kor = re.compile('[가-힣]+') #한국어 단어 개수를 비교해서 그래도 최소한의 단어가 겹치면 맞는 것으로 간주
    mv_set = set(kor.findall(mv))
    kor_title_set = set(kor.findall(kor_title))
    if len(set(mv_set) & set(kor_title_set)) >= min(len(mv_set),len(kor_title_set)):
        return True
    else:
        return False


# In[173]:


def cineaste_download(mv):
    """다운로드 링크 찾고 다운로드 버튼 누르기"""
    print("function 들어옴.")
    for re_c in [j.get_attribute("href") for j in driver.find_elements_by_css_selector(".view_file_download")]:
        #다운로드 링크 찾고, 다운로드
        if re_c.startswith("http://cineaste.co.kr/bbs/download"):
            driver.get(re_c) # 자막다운로드 제대로되는지.
            print ("downloaded", mv) # 다운로드 받고, 리스트에 추가
            print (driver.find_elements_by_css_selector("div.bg-white h3 a")[0])
            driver.get(driver.find_elements_by_css_selector("div.bg-white h3 a")[0].get_attribute("href"))
            #yesdown.append(mv)
            filename(mv,index)
            break


# In[174]:


def unzip():
    with zipfile.ZipFile(filename,"r") as zip_ref:
        zip_ref.extractall("targetdir")


# In[183]:


## 준비 : 다운로드 경로를 subtitle 설정

driver = webdriver.Chrome()


# In[184]:


yesdown=[] # 다운 받은 리스트 
nodown=[] # 노다운 리스트 


# In[185]:


for index, mv in enumerate(real_title_list_ENG[3780:],start=3780):# 이 index는 해당 한국 영화 제목을 찾기 위해 쓰임
    
    if type(mv)==np.ndarray: #사실 나중에 DB에서 전처리 잘하면 필요 없어지는 코드
        mv = mv[-1]
    if not index+1 in zero_movie_key:
        print("\n", mv)
        #씨네스트만 검색한 상태.
        rand_value = randint(2,3)
        time.sleep(rand_value)
        try:
            driver.get("https://www.google.com/search?rlz=1C1SQJL_koKR830KR830&ei=w8xGXZ-rDua2mAWWhJzYCw&q=%EC%94%A8%EB%84%A4%EC%8A%A4%ED%8A%B8&oq=%EC%94%A8%EB%84%A4%EC%8A%A4%ED%8A%B8&gs_l=psy-ab.3..35i39j0l9.6570.10159..10359...6.0..3.178.1390.0j10......0....1..gws-wiz.....10..0i131j0i10.USkgaziaPX4&ved=0ahUKEwjfmLiPmenjAhVmG6YKHRYCB7sQ4dUDCAo&uact=5")
        except:
            driver.get("https://www.google.com/search?rlz=1C1SQJL_koKR830KR830&ei=w8xGXZ-rDua2mAWWhJzYCw&q=%EC%94%A8%EB%84%A4%EC%8A%A4%ED%8A%B8&oq=%EC%94%A8%EB%84%A4%EC%8A%A4%ED%8A%B8&gs_l=psy-ab.3..35i39j0l9.6570.10159..10359...6.0..3.178.1390.0j10......0....1..gws-wiz.....10..0i131j0i10.USkgaziaPX4&ved=0ahUKEwjfmLiPmenjAhVmG6YKHRYCB7sQ4dUDCAo&uact=5")

        #임시로 1~2초 기다림(robot 방지)

        driver.find_element_by_id("nqsbq").send_keys(mv) #씨네스트 검색창에다 영화이름

        driver.find_element_by_css_selector(".ojyYHb > .ab_button").click() #검색버튼 누름

        cinequeue = [i for i in [i.get_attribute("href") for i in 
                                 driver.find_elements_by_css_selector(".rc > .r > a")] if i.startswith("http://cineaste.co.kr/bbs/board.php?bo_table=psd_caption")]

        if cinequeue:
            cinelink = cinequeue[0]
            print("씨네스트 자막 게시판 링크 : ",cinelink)
            driver.get(cinelink)
            try:
                cine_title = checkCineBoard(cinelink)
                if english_title_match(cine_title, mv):
                    print("영어 제목 일치")
                    cineaste_download(mv)
                    alert.accept()
                    yesdown.append(mv)
                elif(korean_title_match(mv,title_list_KOR[index])):
                    print("한글 제목 일치")
                    cineaste_download(mv)
                    alert.accept()
                    yesdown.append(mv) 
                else:
                    print("한국어로 검색해도 없다")
                    nodown.append(mv)
            except:
                # 이경우는 게시판있다고해서 들어갔는데, 자막 삭제된경우에 들어감. 
                nodown.append(mv)
                print("자막 게시글 삭제됨")
        else:
            nodown.append(mv)
            print("씨네스트 링크가 없다")
    else:
        continue


# In[186]:


driver.close()

