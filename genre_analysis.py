#!/usr/bin/env python
# coding: utf-8

# In[5]:


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# In[6]:


import pandas as pd


# In[10]:


def mili_to_min(millis):
    mins=(millis/1000)/60

    return round(mins, 3)


# In[11]:


def get_subtitle1_list():

    cur.execute("select distinct movie_key from Subtitles")
    subtitle1_list = cur.fetchall()
    subtitle1_list = [_[0] for _ in subtitle1_list]
    
    return subtitle1_list


# In[12]:


def get_runtime(movie_key):
    """해당 영화에 대한 러닝타임(분) 가져오기"""
    cur.execute("select runtime from NVmovie where id = :Id", {"Id": movie_key})

    runtime = cur.fetchone()
    runtime = int(re.findall("(\d+)", runtime[0])[0])
    
    return runtime


# In[13]:


def create_movie_df(movie_key):
    """해당 영화에 대한 pandas dataframe 만들기"""
    cur.execute("select start_time, lines, h_index from REALQUOTE where movie_key = :Id", {"Id": movie_key})
    quotes = cur.fetchall()
    quotes = sorted(quotes, key=operator.itemgetter(0))
    
    if movie_key in subtitle1_list:
        cur.execute("select start_time, lines from Subtitles where movie_key = :Id", {"Id": movie_key})
        script = cur.fetchall()
    else:
        cur.execute("select start_time, lines from Subtitles2 where movie_key = :Id", {"Id": movie_key})
        script = cur.fetchall()
    #print(len(quotes), len(script))
    
    quote_df = pd.DataFrame(quotes, columns =['time', 'lines', 'g-index'])
    quote_df.time= quote_df.time.apply(lambda x: mili_to_min(x))
    
    script_df = pd.DataFrame(script, columns =['time', 'lines'])
    script_df.time= script_df.time.apply(lambda x: mili_to_min(int(x)))
    
    runtime = get_runtime(movie_key)
    
    bins = list(map(lambda x:x*runtime, [round(float(_), 3) for _ in np.arange(0,1.1,0.125)]))
    stage_labels = ["stage"+str(_+1) for _ in np.arange(0,8,1)]
    


    merged_df = pd.merge(script_df, quote_df, how='outer')
    merged_df['g-index'] = merged_df['g-index'].fillna(0)
    stages = pd.cut(merged_df['time'], bins, labels=stage_labels)
    merged_df = merged_df.join(stages.to_frame("stage"))
    merged_df.insert(0, "movie_key", movie_key)
    
    return merged_df


# In[14]:


def get_stages_mean(movie_df):
    """stage별 명대사 품질 평균 pandas dataframe 리턴 함수"""
    stage_mean = movie_df["g-index"].groupby(movie_df["stage"]).mean()
    stage_sum = stage_mean.sum()
    stages_mean = (stage_mean/stage_sum).to_frame("stages_mean")
    stages_mean['movie_key'] = movie_df['movie_key'][0]
    stages_mean.reset_index(level=0, inplace=True)
    #stages_mean['stages_mean'].fillna(0, inplace=True)
    stages_mean = stages_mean[['movie_key', 'stage', 'stages_mean']]
    return stages_mean


# In[15]:


def genre_analysis(genre_list):
    """꼭 장르별일 필요는 없다"""
    #subtitle1_list = get_subtitle1_list()
    genre_pd_list = list()   
    for _ in genre_list:
        genre_pd_list.append(create_movie_df(_))
        
    genre_concat = pd.concat(genre_pd_list)
    
    genre_stage_mean_list = list()
    for _ in genre_pd_list:
        genre_stage_mean_list.append(get_stages_mean(_))
        
    genre_stage_concat = pd.concat(genre_stage_mean_list)
    
    return genre_concat, genre_stage_concat
    


# In[16]:


def stage_analysis(genre_stage_concat, genre_name):
    """df info와 pyplot 그래프 확인하는 함수"""
    import matplotlib.pyplot as plt 
    
    print(genre_stage_concat.groupby([genre_stage_concat["movie_key"], genre_stage_concat["stage"]]).mean().info())
    fig = plt.figure()
    plt.plot(list(genre_stage_concat['stage'].unique()),genre_stage_concat.groupby(genre_stage_concat["stage"]).mean()['stages_mean'])
    


# In[17]:


from scipy.stats import sem, t
from scipy import mean

def confidence_interval(data, confidence):
    """confidence는 0~1사이 값"""
    n = len(data)
    m = mean(data)
    std_err = sem(data)
    h = std_err * t.ppf((1 + confidence) / 2, n - 1)

    start = round(m - h, 3)
    m = round(m, 3)
    end = round(m + h, 3)
    
    return start, m, end


# In[18]:


genre_list = ['액션', '코미디', '드라마', '멜로/로맨스',' 스릴러', 'SF', '판타지', '애니메이션', '모험',' 미스터리', '범죄']


# In[373]:


from collections import defaultdict

def error_band(genre_stage_concat, confidence):
    error_band_plot_dict = defaultdict(list)
    stage_labels = ["stage"+str(_+1) for _ in np.arange(0,8,1)]
    for _ in stage_labels:
        x = genre_stage_concat.loc[genre_stage_concat["stage"] == str(_)]['stages_mean']

        start, mean, end = confidence_interval(x.dropna(), confidence)
        error_band_plot_dict[_] = [start, mean, end]
        
    return error_band_plot_dict


# In[871]:


action10_coord = list()
for _ in actionList:
    action10_coord.append(error_dict_to_coordinates(error_band(action_stage_concat.loc[action_stage_concat['movie_key']== _], 0.9))[2])


# In[875]:


comedy10_coord = list()
for _ in comedyList:
    comedy10_coord.append(error_dict_to_coordinates(error_band(comedy_stage_concat.loc[comedy_stage_concat['movie_key']== _], 0.9))[2])


# In[876]:


drama10_coord = list()
for _ in dramaList:
    drama10_coord.append(error_dict_to_coordinates(error_band(drama_stage_concat.loc[drama_stage_concat['movie_key']== _], 0.9))[2])


# In[877]:


romance10_coord = list()
for _ in romanceList:
    romance10_coord.append(error_dict_to_coordinates(error_band(romance_stage_concat.loc[romance_stage_concat['movie_key']== _], 0.9))[2])


# In[878]:


thriller10_coord = list()
for _ in thrillerList:
    thriller10_coord.append(error_dict_to_coordinates(error_band(thriller_stage_concat.loc[thriller_stage_concat['movie_key']== _], 0.9))[2])


# In[879]:


SF10_coord = list()
for _ in SFList:
    SF10_coord.append(error_dict_to_coordinates(error_band(SF_stage_concat.loc[SF_stage_concat['movie_key']== _], 0.9))[2])


# In[880]:


fantasy10_coord = list()
for _ in fantasyList:
    fantasy10_coord.append(error_dict_to_coordinates(error_band(fantasy_stage_concat.loc[fantasy_stage_concat['movie_key']== _], 0.9))[2])


# In[881]:


animation10_coord = list()
for _ in animationList:
    animation10_coord.append(error_dict_to_coordinates(error_band(animation_stage_concat.loc[animation_stage_concat['movie_key']== _], 0.9))[2])


# In[882]:


adventure10_coord = list()
for _ in adventureList:
    adventure10_coord.append(error_dict_to_coordinates(error_band(adventure_stage_concat.loc[adventure_stage_concat['movie_key']== _], 0.9))[2])


# In[883]:


mystery10_coord = list()
for _ in mysteryList:
    mystery10_coord.append(error_dict_to_coordinates(error_band(mystery_stage_concat.loc[mystery_stage_concat['movie_key']== _], 0.9))[2])


# In[884]:


crime10_coord = list()
for _ in crimeList:
    crime10_coord.append(error_dict_to_coordinates(error_band(crime_stage_concat.loc[crime_stage_concat['movie_key']== _], 0.9))[2])


# In[791]:


action_graph = error_dict_to_coordinates(error_band(action_stage_concat, 0.9))


# In[793]:


comedy_graph = error_dict_to_coordinates(error_band(comedy_stage_concat, 0.9))


# In[794]:


drama_graph = error_dict_to_coordinates(error_band(drama_stage_concat, 0.9))


# In[815]:


romance_graph = error_dict_to_coordinates(error_band(romance_stage_concat, 0.9))


# In[795]:


thriller_graph = error_dict_to_coordinates(error_band(thriller_stage_concat, 0.9))


# In[796]:


SF_graph = error_dict_to_coordinates(error_band(SF_stage_concat, 0.9))


# In[797]:


fantasy_graph = error_dict_to_coordinates(error_band(fantasy_stage_concat, 0.9))


# In[798]:


animation_graph = error_dict_to_coordinates(error_band(animation_stage_concat, 0.9))


# In[799]:


adventure_graph = error_dict_to_coordinates(error_band(adventure_stage_concat, 0.9))


# In[800]:


mystery_graph = error_dict_to_coordinates(error_band(mystery_stage_concat, 0.9))


# In[801]:


crime_graph = error_dict_to_coordinates(error_band(crime_stage_concat, 0.9))


# In[789]:


def error_dict_to_coordinates(error_band_dict):
    
    x = list(np.arange(1,9,1))

    y_max = [_[1][2] for _ in error_band_dict.items()]
    y_mean = [_[1][1] for _ in error_band_dict.items()]
    y_min = [_[1][0] for _ in error_band_dict.items()]
    
    return [x, y_max, y_mean, y_min]


# In[375]:


def error_dict_to_coordinates(error_band_dict):
    
    x = list(np.arange(1,9,1))

    y_max = [_[1][2] for _ in error_band_dict.items()]
    y_mean = [_[1][1] for _ in error_band_dict.items()]
    y_min = [_[1][0] for _ in error_band_dict.items()]
    
    return [x, y_max, y_mean, y_min]


# In[420]:


action_stage_concat['genre'] = "액션"


# In[422]:


comedy_stage_concat['genre'] = "코미디"


# In[424]:


drama_stage_concat['genre'] = "드라마"


# In[729]:


romance_stage_concat['genre'] = "멜로/로맨스"


# In[428]:


thriller_stage_concat['genre'] = "스릴러"


# In[430]:


SF_stage_concat['genre'] = "SF"


# In[432]:


fantasy_stage_concat['genre'] = "판타지"


# In[434]:


animation_stage_concat['genre'] = "애니메이션"


# In[436]:


adventure_stage_concat['genre'] = "모험"


# In[438]:


mystery_stage_concat['genre'] = "미스터리"


# In[440]:


crime_stage_concat['genre'] = "범죄"


# ### 1. genre_stage_concat 만들기

# In[719]:


genre_stage_concat = pd.concat([action_stage_concat, comedy_stage_concat, drama_stage_concat, romance_stage_concat, 
                                thriller_stage_concat, SF_stage_concat, fantasy_stage_concat, animation_stage_concat, 
                                adventure_stage_concat, mystery_stage_concat, crime_stage_concat])


# In[720]:


genre_stage_concat["genre_code"] = pd.factorize(genre_stage_concat['genre'])[0]+1


# In[721]:


genre_stage_concat["stage_code"] = pd.factorize(genre_stage_concat['stage'])[0]+1


# In[723]:


genre_stage_concat = genre_stage_concat[['movie_key','stage', 'genre',  'stage_code','genre_code', 'stages_mean']]


# ### 2.  genre_stage_concat 에서 장르별 genre_x 를 만들기

# 액션, 코미디, 드라마, 멜로/로맨스, 스릴러, SF, 판타지, 애니메이션, 모험, 미스터리, 범죄¶

# In[698]:


action_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==1][['movie_key','genre_code','stage_code','stages_mean']]
action_x = action_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
action_x["genre"] = 1


# In[456]:


comedy_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==2][['movie_key','genre_code','stage_code','stages_mean']]
comedy_x = comedy_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
comedy_x["genre"] = 2


# In[731]:


drama_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==3][['movie_key','genre_code','stage_code','stages_mean']]
drama_x = drama_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
drama_x["genre"] = 3


# In[732]:


romance_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==4][['movie_key','genre_code','stage_code','stages_mean']]
romance_x = romance_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
romance_x["genre"] = 4


# In[461]:


thriller_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==5][['movie_key','genre_code','stage_code','stages_mean']]
thriller_x = thriller_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
thriller_x["genre"] = 5


# In[463]:


SF_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==6][['movie_key','genre_code','stage_code','stages_mean']]
SF_x = SF_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
SF_x["genre"] = 6


# In[465]:


fantasy_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==7][['movie_key','genre_code','stage_code','stages_mean']]
fantasy_x = fantasy_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
fantasy_x["genre"] = 7


# In[466]:


animation_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==8][['movie_key','genre_code','stage_code','stages_mean']]
animation_x = animation_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
animation_x["genre"] = 8


# In[467]:


adventure_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==9][['movie_key','genre_code','stage_code','stages_mean']]
adventure_x = adventure_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
adventure_x["genre"] = 9


# In[468]:


mystery_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==10][['movie_key','genre_code','stage_code','stages_mean']]
mystery_x = mystery_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
mystery_x["genre"] = 10


# In[469]:


crime_x = genre_stage_concat.loc[genre_stage_concat['genre_code']==11][['movie_key','genre_code','stage_code','stages_mean']]
crime_x = crime_x.pivot(index = 'movie_key', columns='stage_code', values='stages_mean').dropna()
crime_x["genre"] = 11


# ### 3. genre_x 가져와서 그래프 유사도 계산하기

# In[786]:


# 장르 평균 그래프의 좌표값
action_mean = action_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    action_x[i] = action_x[i].apply(lambda x: abs(x-action_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
action_stage_min_max = list()
for _ in error_band(action_stage_concat, 0.9).keys():
    action_stage_min_max.append(error_band(action_stage_concat, 0.9)[_][2] - error_band(action_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    action_x[i] = action_x[i].apply(lambda x: x/action_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
action_similar_df = action_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

action_similar_df.head()


# In[710]:


# 장르 평균 그래프의 좌표값
comedy_mean = comedy_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    comedy_x[i] = comedy_x[i].apply(lambda x: abs(x-comedy_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
comedy_stage_min_max = list()
for _ in error_band(comedy_stage_concat, 0.9).keys():
    comedy_stage_min_max.append(error_band(comedy_stage_concat, 0.9)[_][2] - error_band(comedy_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    comedy_x[i] = comedy_x[i].apply(lambda x: x/comedy_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
comedy_similar_df = comedy_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

comedy_similar_df.head()


# In[733]:


# 장르 평균 그래프의 좌표값
drama_mean = drama_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    drama_x[i] = drama_x[i].apply(lambda x: abs(x-drama_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
drama_stage_min_max = list()
for _ in error_band(drama_stage_concat, 0.9).keys():
    drama_stage_min_max.append(error_band(drama_stage_concat, 0.9)[_][2] - error_band(drama_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    drama_x[i] = drama_x[i].apply(lambda x: x/drama_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
drama_similar_df = drama_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

drama_similar_df.head()


# In[735]:


# 장르 평균 그래프의 좌표값
romance_mean = romance_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    romance_x[i] = romance_x[i].apply(lambda x: abs(x-romance_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
romance_stage_min_max = list()
for _ in error_band(romance_stage_concat, 0.9).keys():
    romance_stage_min_max.append(error_band(romance_stage_concat, 0.9)[_][2] - error_band(romance_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    romance_x[i] = romance_x[i].apply(lambda x: x/romance_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
romance_similar_df = romance_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

romance_similar_df.head()


# In[821]:


# 장르 평균 그래프의 좌표값
thriller_mean = thriller_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    thriller_x[i] = thriller_x[i].apply(lambda x: abs(x-thriller_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
thriller_stage_min_max = list()
for _ in error_band(thriller_stage_concat, 0.9).keys():
    thriller_stage_min_max.append(error_band(thriller_stage_concat, 0.9)[_][2] - error_band(thriller_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    thriller_x[i] = thriller_x[i].apply(lambda x: x/thriller_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
thriller_similar_df = thriller_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

thriller_similar_df.head()


# In[823]:


# 장르 평균 그래프의 좌표값
SF_mean = SF_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    SF_x[i] = SF_x[i].apply(lambda x: abs(x-SF_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
SF_stage_min_max = list()
for _ in error_band(SF_stage_concat, 0.9).keys():
    SF_stage_min_max.append(error_band(SF_stage_concat, 0.9)[_][2] - error_band(SF_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    SF_x[i] = SF_x[i].apply(lambda x: x/SF_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
SF_similar_df = SF_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

SF_similar_df.head()


# In[825]:


# 장르 평균 그래프의 좌표값
fantasy_mean = fantasy_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    fantasy_x[i] = fantasy_x[i].apply(lambda x: abs(x-fantasy_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
fantasy_stage_min_max = list()
for _ in error_band(fantasy_stage_concat, 0.9).keys():
    fantasy_stage_min_max.append(error_band(fantasy_stage_concat, 0.9)[_][2] - error_band(fantasy_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    fantasy_x[i] = fantasy_x[i].apply(lambda x: x/fantasy_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
fantasy_similar_df = fantasy_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

fantasy_similar_df.head()


# In[827]:


# 장르 평균 그래프의 좌표값
animation_mean = animation_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    animation_x[i] = animation_x[i].apply(lambda x: abs(x-animation_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
animation_stage_min_max = list()
for _ in error_band(animation_stage_concat, 0.9).keys():
    animation_stage_min_max.append(error_band(animation_stage_concat, 0.9)[_][2] - error_band(animation_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    animation_x[i] = animation_x[i].apply(lambda x: x/animation_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
animation_similar_df = animation_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

animation_similar_df.head()


# In[829]:


# 장르 평균 그래프의 좌표값
adventure_mean = adventure_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    adventure_x[i] = adventure_x[i].apply(lambda x: abs(x-adventure_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
adventure_stage_min_max = list()
for _ in error_band(adventure_stage_concat, 0.9).keys():
    adventure_stage_min_max.append(error_band(adventure_stage_concat, 0.9)[_][2] - error_band(adventure_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    adventure_x[i] = adventure_x[i].apply(lambda x: x/adventure_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
adventure_similar_df = adventure_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

adventure_similar_df.head()


# In[831]:


# 장르 평균 그래프의 좌표값
mystery_mean = mystery_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    mystery_x[i] = mystery_x[i].apply(lambda x: abs(x-mystery_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
mystery_stage_min_max = list()
for _ in error_band(mystery_stage_concat, 0.9).keys():
    mystery_stage_min_max.append(error_band(mystery_stage_concat, 0.9)[_][2] - error_band(mystery_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    mystery_x[i] = mystery_x[i].apply(lambda x: x/mystery_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
mystery_similar_df = mystery_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

mystery_similar_df.head()


# In[833]:


# 장르 평균 그래프의 좌표값
crime_mean = crime_x.groupby('genre').mean()


# stage 별 euclidean distance 구하기
for i in np.arange(1,9,1):
    crime_x[i] = crime_x[i].apply(lambda x: abs(x-crime_mean[i].values[0]))

# stage 별 신뢰구간 너비 구하기
crime_stage_min_max = list()
for _ in error_band(crime_stage_concat, 0.9).keys():
    crime_stage_min_max.append(error_band(crime_stage_concat, 0.9)[_][2] - error_band(crime_stage_concat, 0.9)[_][0])

# 구한 신뢰구간 너비로 나누기    
for i in np.arange(1,9,1):
    crime_x[i] = crime_x[i].apply(lambda x: x/crime_stage_min_max[i-1])
    
    
#최종 sort 된 movie_key 리스트    
crime_similar_df = crime_x.drop(columns='genre').sum(axis=1).to_frame('dist_sum').sort_values(['dist_sum'])

crime_similar_df.head()


# ### 흥행성적이랑 합쳐서 top10 추리기

# In[775]:


box_data = pd.read_csv("ver3.box_table.csv", engine='python')
box_data.drop(box_data.columns[0], axis=1, inplace=True)
box_data.drop(columns=["id"], inplace=True)


# In[776]:


box_data.rename(columns={"origin": "audience"}, inplace=True)


# In[784]:


box_data.head()


# In[785]:


action_similar_df = pd.merge(action_similar_df, box_data, on='movie_key')
action_top_10 = action_similar_df.head(10)
action_top_10


# In[707]:


comedy_similar_df = pd.merge(comedy_similar_df, box_data, on='movie_key')
comedy_top_10 = comedy_similar_df.head(10)
comedy_top_10


# In[734]:


drama_similar_df = pd.merge(drama_similar_df, box_data, on='movie_key')
drama_top_10 = drama_similar_df.head(10)
drama_top_10


# In[736]:


romance_similar_df = pd.merge(romance_similar_df, box_data, on='movie_key')
romance_top_10 = romance_similar_df.head(10)
romance_top_10


# In[822]:


thriller_similar_df = pd.merge(thriller_similar_df, box_data, on='movie_key')
thriller_top_10 = thriller_similar_df.head(10)
thriller_top_10


# In[824]:


SF_similar_df = pd.merge(SF_similar_df, box_data, on='movie_key')
SF_top_10 = SF_similar_df.head(10)
SF_top_10


# In[826]:


fantasy_similar_df = pd.merge(fantasy_similar_df, box_data, on='movie_key')
fantasy_top_10 = fantasy_similar_df.head(10)
fantasy_top_10


# In[828]:


animation_similar_df = pd.merge(animation_similar_df, box_data, on='movie_key')
animation_top_10 = animation_similar_df.head(10)
animation_top_10


# In[830]:


adventure_similar_df = pd.merge(adventure_similar_df, box_data, on='movie_key')
adventure_top_10 = adventure_similar_df.head(10)
adventure_top_10


# In[832]:


mystery_similar_df = pd.merge(mystery_similar_df, box_data, on='movie_key')
mystery_top_10 = mystery_similar_df.head(10)
mystery_top_10


# In[834]:


crime_similar_df = pd.merge(crime_similar_df, box_data, on='movie_key')
crime_top_10 = crime_similar_df.head(10)
crime_top_10


# In[835]:


actionList = list(action_top_10["movie_key"])


# In[836]:


comedyList = list(comedy_top_10["movie_key"])


# In[837]:


dramaList = list(drama_top_10["movie_key"])


# In[838]:


romanceList = list(romance_top_10["movie_key"])


# In[839]:


thrillerList = list(thriller_top_10["movie_key"])


# In[840]:


SFList = list(SF_top_10["movie_key"])


# In[841]:


fantasyList = list(fantasy_top_10["movie_key"])


# In[842]:


animationList = list(animation_top_10["movie_key"])


# In[843]:


adventureList = list(adventure_top_10["movie_key"])


# In[844]:


mysteryList = list(mystery_top_10["movie_key"])


# In[845]:


crimeList = list(crime_top_10["movie_key"])

