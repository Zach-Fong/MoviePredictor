from ast import keyword
import pandas as pd
import matplotlib.pyplot as plt
from setuptools import sic
plt.style.use('fivethirtyeight')
import seaborn as sns
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')
import base64
import io
# from scipy.misc import imread
import codecs
import operator
from scipy import spatial
import csv
from csv import writer
import requests
# from IPython.display import HTML

#source: https://www.kaggle.com/code/ash316/what-s-my-score
#Based on the above link. This application dynamically adds and cleans searched movies to the csv files tmdb_5000_movies and tmdb_5000_credits
#add to database with updated columns (use top 4 cast/keywords/etc)

def director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']

def xstr(s):
    if s is None:
        return ''
    return str(s)

def add_and_clean(genreList, directorList, castList, words_list):

    movies=pd.read_csv('./data/tmdb_5000_movies.csv')
    mov=pd.read_csv('./data/tmdb_5000_credits.csv')

    # changing the genres column from json to string
    movies['genres']=movies['genres'].apply(json.loads)
    for index,i in zip(movies.index,movies['genres']):
        list1=[]
        for j in range(len(i)):
            list1.append((i[j]['name']))# the key 'name' contains the name of the genre
        movies.loc[index,'genres']=str(list1)
        
    # changing the keywords column from json to string
    movies['keywords']=movies['keywords'].apply(json.loads)
    for index,i in zip(movies.index,movies['keywords']):
        list1=[]
        for j in range(len(i)):
            list1.append((i[j]['name']))
        movies.loc[index,'keywords']=str(list1)
        
    ## changing the production_companies column from json to string
    movies['production_companies']=movies['production_companies'].apply(json.loads)
    for index,i in zip(movies.index,movies['production_companies']):
        list1=[]
        for j in range(len(i)):
            list1.append((i[j]['name']))
        movies.loc[index,'production_companies']=str(list1)
        
    # changing the production_countries column from json to string    
    movies['production_countries']=movies['production_countries'].apply(json.loads)
    for index,i in zip(movies.index,movies['production_countries']):
        list1=[]
        for j in range(len(i)):
            list1.append((i[j]['name']))
        movies.loc[index,'production_countries']=str(list1)
        
    # changing the cast column from json to string
    mov['cast']=mov['cast'].apply(json.loads)
    for index,i in zip(mov.index,mov['cast']):
        list1=[]
        for j in range(len(i)):
            list1.append((i[j]['name']))
        mov.loc[index,'cast']=str(list1)

    # changing the crew column from json to string    
    mov['crew']=mov['crew'].apply(json.loads)
    mov['crew']=mov['crew'].apply(director)
    mov.rename(columns={'crew':'director'},inplace=True)

    movies=movies.merge(mov,left_on='id',right_on='movie_id',how='left')# merging the two csv files
    movies=movies[['id','original_title','genres','cast','vote_average','director','keywords']]

    movies['genres']=movies['genres'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['genres']=movies['genres'].str.split(',')

    #sort genres
    for i,j in zip(movies['genres'],movies.index):
        list2=[]
        list2=i
        list2.sort()
        movies.loc[j,'genres']=str(list2)
    movies['genres']=movies['genres'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['genres']=movies['genres'].str.split(',')

    #find all genres
    for index, row in movies.iterrows():
        genres = row["genres"]
        for genre in genres:
            if genre not in genreList:
                genreList.append(genre)
    genreList[:10]

    movies['genres_bin'] = movies['genres']

    movies['cast']=movies['cast'].str.strip('[]').str.replace(' ','').str.replace("'",'').str.replace('"','')
    movies['cast']=movies['cast'].str.split(',')

    #keep 4 most important actors for each movie sorted
    for i,j in zip(movies['cast'],movies.index):
        list2=[]
        list2=i[:4]
        movies.loc[j,'cast']=str(list2)
    movies['cast']=movies['cast'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['cast']=movies['cast'].str.split(',')
    for i,j in zip(movies['cast'],movies.index):
        list2=[]
        list2=i
        list2.sort()
        movies.loc[j,'cast']=str(list2)
    movies['cast']=movies['cast'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['cast']=movies['cast'].str.split(',')

    #keep track of every actor (taken from every movies top 4)
    for index, row in movies.iterrows():
        cast = row["cast"]
        for i in cast:
            if i not in castList:
                castList.append(i)

    movies['cast_bin'] = movies['cast']

    #clean directors and add binary
    movies['director']=movies['director'].apply(xstr)

    for i in movies['director']:
        if i not in directorList:
            directorList.append(i)

    movies['director_bin'] = movies['director']

    #clean keywords
    movies['keywords']=movies['keywords'].str.strip('[]').str.replace(' ','').str.replace("'",'').str.replace('"','')
    movies['keywords']=movies['keywords'].str.split(',')
    for i,j in zip(movies['keywords'],movies.index):
        list2=[]
        list2=i
        movies.loc[j,'keywords']=str(list2)
    movies['keywords']=movies['keywords'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['keywords']=movies['keywords'].str.split(',')
    for i,j in zip(movies['keywords'],movies.index):
        list2=[]
        list2=i
        list2.sort()
        movies.loc[j,'keywords']=str(list2)
    movies['keywords']=movies['keywords'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['keywords']=movies['keywords'].str.split(',')
    #keyword list
    for index, row in movies.iterrows():
        genres = row["keywords"]
        for genre in genres:
            if genre not in words_list:
                words_list.append(genre)

    #binary conversion of keywords, remove movies with score 0 and no director
    movies['words_bin'] = movies['keywords']
    movies=movies[(movies['vote_average']!=0)]
    movies=movies[movies['director']!='']

    # movies=movies[['original_title','genres','vote_average','genres_bin','cast_bin','id','director','director_bin','words_bin']]
    movies=movies[['original_title','vote_average','genres_bin','cast_bin','id','director_bin','words_bin']]

    return movies

def convert():

    genreList = []
    castList = []
    directorList = []
    words_list = []

    movies = add_and_clean(genreList, castList, directorList, words_list)
    movies.to_csv("./data/tmdb_dynamic.csv", encoding='utf-8', index=False)

def addNew(movie_to_add):

    api_key = 'api_key=27989ba887194f26874a5e95813460ab'
    api_search = 'https://api.themoviedb.org/3/search/movie?'
    api_movie = 'https://api.themoviedb.org/3/movie/'
    search_url = api_search + api_key + "&language=en-US&query=" + movie_to_add + "&page=1&include_adult=false"
    search_response = requests.get(search_url)

    movie_id = search_response.json()["results"][0]["id"]
    movie_url = api_movie + str(movie_id) + "?" + api_key + "&language=en-US"
    credit_url = api_movie + str(movie_id) + "/credits?" + api_key + "&language=en-US"
    movie_response = requests.get(movie_url)
    credit_response = requests.get(credit_url)
    keywords_url = api_movie + str(movie_id) + "/keywords?" + api_key + "&language=en-US"
    keywords_response = requests.get(keywords_url)

    json_movie = movie_response.json()
    json_credits = credit_response.json()
    json_keywords = keywords_response.json()

    data_movies = ''
    data_mov = ''

    all_movies = pd.read_csv('./data/tmdb_dynamic.csv')

    not_in = True
    for cur_movie_id in all_movies.id:
        if cur_movie_id == json_movie["id"]:
            not_in = False
            print("Did not add: " + json.dumps(json_movie["original_title"]))
            return
    if not_in:
        data_movies = json.dumps(json_movie["budget"]) + '|' + json.dumps(json_movie["genres"]) + '|' + '|' + json.dumps(json_movie["id"]) + '|' + json.dumps(json_keywords["keywords"])\
            + '|' + json.dumps(json_movie["original_language"]) + '|' + json.dumps(json_movie["original_title"]) + '|' + '|' + json.dumps(json_movie["popularity"]) + '|' + \
            json.dumps(json_movie["production_companies"]) + '|' + json.dumps(json_movie["production_countries"]) + '|' + str(json_movie["release_date"]) + '|' + \
            json.dumps(json_movie["revenue"]) + '|' + json.dumps(json_movie["runtime"]) + '|' + json.dumps(json_movie["spoken_languages"]) + '|' + '|' + '|' + json.dumps(json_movie["title"]) \
            + '|' + json.dumps(json_movie["vote_average"]) + '|' + json.dumps(json_movie["vote_count"])
        data_mov = json.dumps(json_credits["id"]) + '|' + json.dumps(json_movie["original_title"]) + '|' + json.dumps(json_credits["cast"]) + '|' + json.dumps(json_credits["crew"])

    temp_movies = io.StringIO(data_movies)
    movies = pd.read_csv(temp_movies, sep="|", names=["budget","genres","homepage","id","keywords","original_language","original_title","overview","popularity","production_companies","production_countries","release_date","revenue","runtime","spoken_languages","status","tagline","title","vote_average","vote_count"])
    temp_mov = io.StringIO(data_mov)
    mov = pd.read_csv(temp_mov, sep="|", names=["movie_id","title","cast","crew"])

    #*****STARTING HERE CONVERT INDIVIDUAL STRING TO CSV COMPACT*****

    # changing the genres column from json to string
    movies['genres']=movies['genres'].apply(json.loads)
    for index,i in zip(movies.index,movies['genres']):
        list1=[]
        for j in range(len(i)):
            list1.append((i[j]['name']))# the key 'name' contains the name of the genre
        movies.loc[index,'genres']=str(list1)
        
    # changing the keywords column from json to string
    movies['keywords']=movies['keywords'].apply(json.loads)
    for index,i in zip(movies.index,movies['keywords']):
        list1=[]
        for j in range(len(i)):
            list1.append((i[j]['name']))
        movies.loc[index,'keywords']=str(list1)
        
    ## changing the production_companies column from json to string
    movies['production_companies']=movies['production_companies'].apply(json.loads)
    for index,i in zip(movies.index,movies['production_companies']):
        list1=[]
        for j in range(len(i)):
            list1.append((i[j]['name']))
        movies.loc[index,'production_companies']=str(list1)
        
    # changing the production_countries column from json to string    
    movies['production_countries']=movies['production_countries'].apply(json.loads)
    for index,i in zip(movies.index,movies['production_countries']):
        list1=[]
        for j in range(len(i)):
            list1.append((i[j]['name']))
        movies.loc[index,'production_countries']=str(list1)
        
    # changing the cast column from json to string
    mov['cast']=mov['cast'].apply(json.loads)
    for index,i in zip(mov.index,mov['cast']):
        list1=[]
        for j in range(len(i)):
            list1.append((i[j]['name']))
        mov.loc[index,'cast']=str(list1)

    # changing the crew column from json to string    
    mov['crew']=mov['crew'].apply(json.loads)
    mov['crew']=mov['crew'].apply(director)
    mov.rename(columns={'crew':'director'},inplace=True)

    movies=movies.merge(mov,left_on='id',right_on='movie_id',how='left')# merging the two csv files
    movies=movies[['id','original_title','genres','cast','vote_average','director','keywords']]

    movies['genres']=movies['genres'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['genres']=movies['genres'].str.split(',')

    #sort genres
    for i,j in zip(movies['genres'],movies.index):
        list2=[]
        list2=i
        list2.sort()
        movies.loc[j,'genres']=str(list2)
    movies['genres']=movies['genres'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['genres']=movies['genres'].str.split(',')

    movies['genres_bin'] = movies['genres']

    movies['cast']=movies['cast'].str.strip('[]').str.replace(' ','').str.replace("'",'').str.replace('"','')
    movies['cast']=movies['cast'].str.split(',')

    #keep 4 most important actors for each movie sorted
    for i,j in zip(movies['cast'],movies.index):
        list2=[]
        list2=i[:4]
        movies.loc[j,'cast']=str(list2)
    movies['cast']=movies['cast'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['cast']=movies['cast'].str.split(',')
    for i,j in zip(movies['cast'],movies.index):
        list2=[]
        list2=i
        list2.sort()
        movies.loc[j,'cast']=str(list2)
    movies['cast']=movies['cast'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['cast']=movies['cast'].str.split(',')

    movies['cast_bin'] = movies['cast']

    #clean directors and add binary
    movies['director']=movies['director'].apply(xstr)

    movies['director_bin'] = movies['director']

    #clean keywords
    movies['keywords']=movies['keywords'].str.strip('[]').str.replace(' ','').str.replace("'",'').str.replace('"','')
    movies['keywords']=movies['keywords'].str.split(',')
    for i,j in zip(movies['keywords'],movies.index):
        list2=[]
        list2=i
        movies.loc[j,'keywords']=str(list2)
    movies['keywords']=movies['keywords'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['keywords']=movies['keywords'].str.split(',')
    for i,j in zip(movies['keywords'],movies.index):
        list2=[]
        list2=i
        list2.sort()
        movies.loc[j,'keywords']=str(list2)
    movies['keywords']=movies['keywords'].str.strip('[]').str.replace(' ','').str.replace("'",'')
    movies['keywords']=movies['keywords'].str.split(',')

    #binary conversion of keywords, remove movies with score 0 and no director
    movies['words_bin'] = movies['keywords']
    movies=movies[(movies['vote_average']!=0)]
    movies=movies[movies['director']!='']

    # movies=movies[['original_title','genres','vote_average','genres_bin','cast_bin','id','director','director_bin','words_bin']]
    movies=movies[['original_title','vote_average','genres_bin','cast_bin','id','director_bin','words_bin']]

    with open('./data/tmdb_dynamic.csv', 'a') as f:
        movies.to_csv(f, header=False, index=False)
    
def addAllNew(movie_list):
    for movie in movie_list:
        addNew(movie)

addNew('Joker')