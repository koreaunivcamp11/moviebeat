#!/usr/bin/env python
# coding: utf-8

# In[4]:


import numpy as np
import operator
from gensim.models import Word2Vec
import konlpy
from konlpy.tag import Okt

okt = Okt()


# In[58]:


#하위 디렉토리에 word2vec_model 폴더가 생성해야함

def movie_quote_matcher(movie_key, db_script, db_nvquotes):
    """word embedding과 bigram으로 영화 자막과 네이버 명대사를 매칭하는 함수. 
    final_matched 라는 딕셔너리와 , g_index_dict를 리턴한다"""
    
    script_offset = int(db_script[0][0])
    quotes_offset = int(db_nvquotes[0][0])
    
    stoplist=["\n","나", "너", "내", "는", "은", "그", "이", "가", "저","야", "아", "어",'에','게', "을", "를", "다", "좀", "헉", "퍽", "팍", "풋", "슝","쾅", "쿵", "끽"]

    def posedString(string):
        """사용할 tokenizer"""
        return [x[0] for x in okt.pos(string) if not x[1].startswith("Punc") and not x[0] in stoplist]
    
    def quote_model(nvquotes, index):
        """word embedding 한 모델에 없는 단어를 찾는 경우 그것만 건너뛴다"""
        quote = list()
        for _ in posedString(nvquotes[index]):
            try:
                quote.append(model[_])
            except:
                continue
        return np.array(quote)

    
    
    lines = np.array(db_script)[::,1]
    nvquotes = np.array(db_nvquotes)[::,1]
    script = [posedString(_) for _ in lines]
    
    #model을 만든다
    
    model = Word2Vec(script, min_count=1, size=200)
    #model.build_vocab(script)
    model.save(".\\word2vec_model\\" + str(movie_key) + '_model')
    
    sentences = np.array(
    [np.sum(np.array([model[_] for _ in posedString(x)]), axis=0) 
     if len(posedString(x))!=0 else np.zeros(200,)
     for i, x in enumerate(lines)])

    quotes = np.array(
        [np.sum(quote_model(nvquotes, i), axis=0) 
         if len(quote_model(nvquotes, i))!=0 else np.zeros(200,)
         for i, x in enumerate(nvquotes)])
    
    
    from collections import defaultdict

    #key는 자막의 index, value는 일치하는 명대사 index들의 리스트
    matched_dict = defaultdict(list)
    
    # 모든 명대사와 자막에 대한 similarity 값이 들어있는 numpy array
    similarity_table = np.zeros([len(quotes), len(sentences)])


    for i, quote in enumerate(quotes):
      similarity = list()

      query_s = np.linalg.norm(quote)

      for j, sentence in enumerate(sentences):

        length_s = np.linalg.norm(sentence)

        sim =  sentence.dot(quote) / (length_s * query_s)

        if np.isnan(sim):
          sim=0
        similarity.append((j, sim))

      similarity_table[i] = np.array(similarity)[::,1]

      similarity.sort(reverse=True, key = operator.itemgetter(1))

      matched = list()
      for j, sim in similarity[:5]:
        if sim > 0.6:
          matched.append((j, sim))
        else:
          break
        
      for j, sim in matched:
        matched_dict[j].append(i)

    def bigramUmjeol(token, N=2):
        """띄어쓰기 빼고 다 붙여서 음절단위의 bigram을 만든다"""
        pattern = re.compile(r'[^가-힣A-Za-z]')
        token = re.sub(pattern, '', token)
        tokens = list(token)
        ngram = list()
        for i in range(len(tokens)-(N-1)):
            ngram.append("".join(tokens[i:i+N]))
        return ngram
    
    
    import re
    from functools import reduce
    # 전체 자막에서 한줄당 bigram의 개수의 평균
    avg_len = (len(reduce(lambda x, y: x + y, [re.sub(re.compile(r'[^가-힣A-Za-z]'), '', _) 
                                               for _ in lines]))-len(lines))/len(lines)
    
    
    def bigramMatch(avg_len, sentence, quote):
        """음절 단위 bigram으로 매칭되는 정도를 계산한 값으로 return 하는 함수"""
        quote_set = set(bigramUmjeol(quote))
        sentence_set = set(bigramUmjeol(sentence))
        K = (0.25 + 0.75*(len(quote_set)/avg_len))
        return len(sentence_set.intersection(quote_set))*K
    

    #최종 매치된 딕셔너리. key는 자막의 index, value는 일치하는 명대사 index들의 리스트
    final_matched = defaultdict(list)
    # bigram 점수가 0.5 인 것들의 (명대사 index, 자막index) 리스트
    non_bmatch = list()
    
    for _ in matched_dict.keys():

      for q in matched_dict[_]:
        b = bigramMatch(avg_len, lines[_], nvquotes[q])
        if b>0.5:
            final_matched[_+script_offset].append(q+quotes_offset)
            
        else:
            non_bmatch.append((q, _))
            similarity_table[q][_] = 0
            
    def g_index_func(sim_table, script_offset):
        """g-index 산출 함수"""
        index_dict = dict()

        category = np.arange(0.8, 0.6, -0.05)
        g_index_table = np.zeros((len(category),len(sim_table[1]))) 

        for k in range(len(sim_table[1])):      
            for j in sim_table[:,k]:           
                for n,_ in enumerate(category):   
                    if j > float(_) :
                        g_index_table[n][k] += 1
                        break
            g = 0
            for n,_ in enumerate(category):    # g_index 구하기

                g += g_index_table[n][k]
                if (n+1)**2 > g:
                    if n==0:
                        g_index = 0
                    else:
                        g_index = n
                    break
                else:
                    if n==len(category)-1:
                        g_index = len(category) 
            index_dict[k+script_offset] = g_index
        return index_dict       

    g_index_dict = g_index_func(similarity_table, script_offset)
            
    return final_matched, g_index_dict


# In[5]:


import sqlite3
con=sqlite3.connect('FINAL_MOVIEBEAT.db')
cur=con.cursor()


# In[6]:


cur.execute("select DISTINCT movie_key from Subtitles2")
movie_key_list = cur.fetchall()


# In[7]:


def get_subtitle1_list():

    cur.execute("select distinct movie_key from Subtitles")
    subtitle1_list = cur.fetchall()
    subtitle1_list = [_[0] for _ in subtitle1_list]
    
    return subtitle1_list

subtitle1_list = get_subtitle1_list()


# In[73]:


for key in movie_key_list:
    i = key[0]

    #subtitles에서 i번째 영화의 자막을 가져온다
    if movie_key in subtitle1_list:
        cur.execute("select id, lines, start_time from Subtitles where movie_key = :movie_key", {"movie_key": i})
        db_script = cur.fetchall()
    else:
        cur.execute("select id, lines, start_time from Subtitles2 where movie_key = :movie_key", {"movie_key": i})
        db_script = cur.fetchall()

    
    # NVquotes에서 명대사를 가져온다
    cur.execute("select id, quote from NVquotes where movie_key= :movie_key", {"movie_key": i})
    db_quotes = cur.fetchall()

    try:
        match_dict, g_index_dict = movie_quote_matcher(i, np.array(db_script)[::,[0,1]], db_quotes)
        print(i, " quote-matched")

        script_offset = int(db_script[0][0])
        quotes_offset = int(db_quotes[0][0])

        for _ in match_dict.keys():

            cur.execute("INSERT INTO REALQUOTE(movie_key, subtitle_key, start_time, lines, h_index) VALUES(?,?,?,?,?)",
                        [i, _, \
                         int(db_script[_-script_offset][2]), \
                         db_script[_-script_offset][1], (g_index_dict[_]+1)])
        
        print(i, " executed")
        
    except:
        print(i, " pass")
        pass

    con.commit()
    


# In[68]:


cur.close()


# In[69]:


con.close()

