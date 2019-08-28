#!/usr/bin/env python
# coding: utf-8

# In[11]:


import os
import re

def combine(folderpath):
    """ 여러 종류의 자막 파일을 txt 파일로 만드는 함수
    """
    count = 0 
    filepath = os.path.abspath(folderpath)
   
    file_list = os.listdir(filepath)
   
    file_list = [i for i in file_list if i.split(".")[-1]=="txt" or i.split(".")[-1]=="txt"]

    file_list.sort(key=lambda v: v.lower())
    all_sub = list()
    last_time = smi(os.path.abspath(filepath+"/"+file_list[0]))[-1][0]
    for i in file_list:
        if count == 0:
            all_sub = smi(os.path.abspath(filepath+"/"+i))
            count += 1
        else:
            for j in smi(os.path.abspath(filepath+"/"+i)):
                all_sub.append((j[0]+last_time,j[1]))
            last_time = all_sub[-1][0]
    return all_sub


# In[2]:



def srt(moviename):
    """확장자가 srt인 자막 파일을 대사 한 줄씩 나누는 함수
    """
    
    line=list()
    
    try:
        with open(moviename,'rt') as f:
            line=f.readlines()
    except:
        with open(moviename,'rt',encoding='utf-8') as f:
            line=f.readlines()
    time= re.compile('^(\d{2}:){2}\d{2}')   #대사가 몇초에 나오는지 매치
    end_cell=re.compile('^\n')             #srt 자막 형식상 한 대사가 끝나면 한줄을 띄게 하는데 그걸 잡아내기위함.
    no_n=re.compile("\n")                  #대사들 중에서 \n을 없앨때 사용
    doublekkuk = re.compile(r"\<.+?\>\n\<.+?\>")
    kkukswei = re.compile(r"\<.+?\>")

    quote=list()
    switch=0 
    string=list()
    for _ in line: 
        if switch==0 and time.search(_): 
            temp_time=time.search(_).group()
            temp_list=temp_time.split(":")
            temp_time=int(temp_list[0])*3600000+int(temp_list[1])*60000+int(temp_list[2])*1000
            switch=1 
            continue
        elif switch==1:
            if end_cell.search(_): 
                quote.append((temp_time," ".join(string))) 
                string=list()
                switch=0
            else:
                 string.append(kkukswei.sub("", no_n.sub("",(doublekkuk.sub("", _)))))
    return quote
   
    
def smi(moviename):
    """확장자가 smi인 자막 파일을 대사 한 줄씩 나누는 함수
    """
    
    line=list()
    try:
        with open(moviename,'rt') as f:
            line=f.readlines()
    except:
        with open(moviename,'rt',encoding='utf-8') as f:
            line=f.readlines()
   
    time = re.compile(r'(<.+ .*=\d+>).*(<. .*=.*?>).*')
    re_time=re.compile(r'(<.+ .*=\d+>).*(<. .*=.*?>)')
    time_end = re.compile(r'(<.+ .*=\d+>).*(<. .*=.*?>).*&nbsp.*') 
    time_num=re.compile('[^\d]+')
    no_n=re.compile(r"<br>|\n")
    doublekkuk = re.compile(r"\<.+?\>\n\<.+?\>")
    kkukswei = re.compile(r"\<.+?\>")
    nbsp=re.compile(r"&nbsp.*")

    switch=0
    quote=list()
    temp_time=0
    switch=0
    quote=list()
    for _ in line:
        if time_end.search(_):
            if switch!=1: #위에 시작이 안나왔는데 nbsp가 나온경우 
                continue
            else:
                quote.append((int(temp_time)," ".join(string)))
                switch=0
                continue
        elif time.search(_):
            if switch==0:
                string=list()
                temp_time=re_time.search(_).group(1)
                temp_time=time_num.sub("",temp_time)
                string.append(nbsp.sub("",kkukswei.sub("", no_n.sub("",(doublekkuk.sub("", re_time.sub("",_)))))))
                switch=1
            else:
                quote.append((int(temp_time)," ".join(string)))
                string=list()
                temp_time=re_time.search(_).group(1)
                temp_time=time_num.sub("",temp_time)
                string.append(nbsp.sub("",kkukswei.sub("", no_n.sub("",(doublekkuk.sub("", re_time.sub("",_)))))))
                switch=1
        else:
            if switch==1:
                string.append(nbsp.sub("",kkukswei.sub("", no_n.sub("",(doublekkuk.sub("", _))))))

    return quote


# In[12]:


import sqlite3

con=sqlite3.connect('FINAL_MOVIEBEAT_DB.db')
cur=con.cursor()


# In[4]:


fuck=list()


# In[9]:


def txt_2_db():
    """ txt 파일을 DB에 넣는 함수
    """
    filepath = os.path.abspath("C:\\Users\\dlekw\\Desktop\\cd1")
    download_file_list = [f for f in os.listdir(filepath)]
    id_pattern= re.compile('^\d+')
    print(len(download_file_list))
    for _ in download_file_list:

        mov_key=int(id_pattern.findall(_)[0])

        try:
            if _.split(" ")[1]=="smi" or _.split(" ")[1]=="crdownload":

                f=smi(os.path.abspath(filepath+"\\"+_))
                for line in f:
                    cur.execute("insert into Subtitles2(movie_key,start_time,lines,is_real) Values(?,?,?,?)",
                                [mov_key,line[0],line[1],0])
                    con.commit()
            elif _.split(" ")[1]=="srt":

                f=srt(os.path.abspath(filepath+"\\"+_))
                for line in f:
                    cur.execute("insert into Subtitles2(movie_key,start_time,lines,is_real) Values(?,?,?,?)",
                                [mov_key,line[0],line[1],0])
                    con.commit()
        except:
            print(_)
            fuck.append(_)


# In[13]:


def zip_2_db():
    """ zip파일 안에 들어가서 합치고 DB에 넣는 함수
    """
    
    filepath = os.path.abspath("C:\\Users\\dlekw\\Desktop\\zip")
    download_file_list = [f for f in os.listdir(filepath)]

    id_pattern= re.compile('^\d+')
    for _ in download_file_list:

        mov_key=int(id_pattern.findall(_)[0])


        try:
            f=combine(os.path.abspath(filepath+"\\"+_))
            for line in f:
                cur.execute("insert into Subtitles2(movie_key,start_time,lines,is_real) Values(?,?,?,?)",[mov_key,line[0],line[1],0])
                con.commit()
        except:
            print(_)
            fuck.append(_)
 


# In[14]:


zip_2_db()

