from ast import keyword
from ctypes import sizeof
from ast import literal_eval
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
from time import time, ctime
# from IPython.display import HTML

#source: https://www.kaggle.com/code/ash316/what-s-my-score
#Uses the converData/tmdb_dynamic data and uses knn regression to predict most similar movies

#return a binary conversion of the list
def binaryGenre(genre_list, genreList):
    binaryList = []
    for genre in genreList:
        if genre in genre_list:
            binaryList.append(1)
        else:
            binaryList.append(0)
    return binaryList

def binaryCast(cast_list, castList):
    binaryList = []
    for cast in castList:
        if cast in cast_list:
            binaryList.append(1)
        else:
            binaryList.append(0)
    return binaryList

def binaryDirector(director_list, directorList):
    binaryList = []
    for direct in directorList:
        if direct in director_list:
            binaryList.append(1)
        else:
            binaryList.append(0)
    return binaryList

def binaryKeyword(words, words_list):
    binaryList = []
    for genre in words_list:
        if genre in words:
            binaryList.append(1)
        else:
            binaryList.append(0)
    return binaryList

#find director
def director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']

#returns empty string on entries that don't exist
def xstr(s):
    if s is None:
        return ''
    return str(s)

#finding similarity using cosine distance
def Similarity(movieId1, movieId2, movies):
    a = movies.loc[movies['id'] == movieId1]
    b = movies.loc[movies['id'] == movieId2]
    
    genresA = a['genres_bin'].tolist()[0]
    genresB = b['genres_bin'].tolist()[0]
    genreDistance = spatial.distance.cosine(genresA, genresB)
    
    scoreA = a['cast_bin'].tolist()[0]
    scoreB = b['cast_bin'].tolist()[0]
    scoreDistance = spatial.distance.cosine(scoreA, scoreB)
    
    directA = a['director_bin'].tolist()[0]
    directB = b['director_bin'].tolist()[0]
    directDistance = spatial.distance.cosine(directA, directB)
    
    wordsA = a['words_bin'].tolist()[0]
    wordsB = b['words_bin'].tolist()[0]
    wordsDistance = spatial.distance.cosine(wordsA, wordsB)

    #weighting of distances can be altered changing how much each distance affects the similarity score
    return genreDistance + directDistance*1.5 + scoreDistance*1.25 + wordsDistance

#uses the score calculated above to find the 10 nearest neighbours (KNN where K=10)
def getNeighbors(baseMovie, K, movies):
    distances = []
    for index, movie in movies.iterrows():
        if movie['id'] != baseMovie['id'].values[0]:
            dist = Similarity(baseMovie['id'].values[0], movie['id'], movies)
            distances.append((movie['id'], dist))
            
    distances.sort(key=operator.itemgetter(1))
    neighbors = []
    for x in range(K):
        neighbors.append(distances[x])

    return neighbors

def configure_movie_data():
    genreList = []
    castList = []
    directorList = []
    keywordsList = []
    movies=pd.read_csv('./data/tmdb_dynamic.csv')

    #find all genres
    for index, row in movies.iterrows():
        genres = row["genres"]
        for genre in literal_eval(genres):
            if genre not in genreList:
                genreList.append(genre)
    #binary conversion for genres
    movies['genres_bin'] = movies['genres'].apply(lambda x: binaryGenre(literal_eval(x), genreList))

    #keep track of every actor (taken from every movies top 4)
    for index, row in movies.iterrows():
        casts = row["cast"]
        for cast in literal_eval(casts):
            if cast not in castList:
                castList.append(cast)
    #binary conversion for actors
    movies['cast_bin'] = movies['cast'].apply(lambda x: binaryCast(literal_eval(x), castList))

    #check empty directors, clean directors, and add binary
    movies['director']=movies['director'].apply(xstr)
    for index, row in movies.iterrows():
        director = row["director"]
        if director not in directorList:
                directorList.append(director)
    movies['director_bin'] = movies['director'].apply(lambda x: binaryDirector(x, directorList))

    #keyword list
    for index, row in movies.iterrows():
        keywords = row["keywords"]
        for keyword in literal_eval(keywords):
            if keyword not in keywordsList:
                keywordsList.append(keyword)
    #binary conversion of keywords
    movies['words_bin'] = movies['keywords'].apply(lambda x: binaryKeyword(literal_eval(x), keywordsList))

    #remove movies with score 0 and no director
    movies=movies[(movies['vote_average']!=0)]
    movies=movies[movies['director']!='']

    return movies

#adds movie/credits data to csv files which contain all json data from themoviedatabase api
#this is so we can have extra data if we ever need to access it
def add_raw_data(json_movie, json_credits, json_keywords):
    movies=pd.read_csv('./data/tmdb_5000_movies.csv')
    not_in = True
    for cur_movie_id in movies.id:
        if cur_movie_id == json_movie["id"]:
            not_in = False
            print("Did not add: " + json.dumps(json_movie["original_title"]))
    if not_in:
        data_movies = json.dumps(json_movie["budget"]) + '|' + json.dumps(json_movie["genres"]) + '|' + '|' + json.dumps(json_movie["id"]) + '|' + json.dumps(json_keywords["keywords"])\
            + '|' + json.dumps(json_movie["original_language"]) + '|' + json.dumps(json_movie["original_title"]) + '|' + '|' + json.dumps(json_movie["popularity"]) + '|' + \
            json.dumps(json_movie["production_companies"]) + '|' + json.dumps(json_movie["production_countries"]) + '|' + str(json_movie["release_date"]) + '|' + \
            json.dumps(json_movie["revenue"]) + '|' + json.dumps(json_movie["runtime"]) + '|' + json.dumps(json_movie["spoken_languages"]) + '|' + '|' + '|' + json.dumps(json_movie["title"]) \
            + '|' + json.dumps(json_movie["vote_average"]) + '|' + json.dumps(json_movie["vote_count"])
        data_credits = json.dumps(json_credits["id"]) + '|' + json.dumps(json_movie["original_title"]) + '|' + json.dumps(json_credits["cast"]) + '|' + json.dumps(json_credits["crew"])
        with open('./data/tmdb_5000_movies.csv', 'a+', newline='') as movies_obj:
            # Create a writer object from csv module
            csv_writer = writer(movies_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(data_movies.split('|'))
        with open('./data/tmdb_5000_credits.csv', 'a+', newline='') as credits_obj:
            # Create a writer object from csv module
            csv_writer = writer(credits_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(data_credits.split('|'))
        print("Added: " + json.dumps(json_movie["original_title"]))

#store only necessary movie data that the knn regression will use
def add_clean_data(json_movie, json_credits, json_keywords):

    #if the movie already exists in the csv it does not add it
    dynamic_movies=pd.read_csv('./data/tmdb_dynamic.csv')
    for cur_movie_id in dynamic_movies.id:
        if cur_movie_id == json_movie["id"]:
            return

    original_title = json_movie["original_title"]
    vote_average = json_movie["vote_average"]
    id = json_movie["id"]
    genres = []
    cast = []
    director = ""
    keywords = []
    count = 0

    #store first 10 genres of the movie
    for i in json_movie["genres"]:
        genres.append(i["name"].replace(' ','').replace("'",''))
        count += 1
        if(count >= 10):
            break
    count = 0
    genres.sort()

    #store first 4 cast members (cast members in json_credits are ordered most important first)
    for i in json_credits["cast"]:
        cast.append(i["name"].replace(' ','').replace("'",''))
        count += 1
        if(count >= 4):
            break
    count = 0
    cast.sort()

    for i in json_credits["crew"]:
        if(i["job"] == 'Director'):
            director = i['name']
            break

    for i in json_keywords["keywords"]:
        keywords.append(i['name'].replace(' ','').replace("'",''))
        count += 1
        if(count >= 4):
            break
    count = 0
    keywords.sort()

    #appends the now clean movie data to the csv file
    newMovie = {'original_title':[original_title],'vote_average':[vote_average],'genres':[genres],'cast':[cast],'id':[id],'director':[director],'keywords':[keywords]}
    datapd = pd.DataFrame(data = newMovie)
    with open('./data/tmdb_dynamic.csv', 'a') as f:
        datapd.to_csv(f, header=False, index=False)

#gets the 10 nearest neighbours and calculates their average with higher weighting on the 5 most similar movies
def whats_my_score(id, movies):
    new_movie = movies.loc[movies['id'] == id]
    K = 10
    count = 0
    avgRating = 0
    neighbors = getNeighbors(new_movie, K, movies)
    allSimilar = ""
    
    for neighbor in neighbors:
        neighborMovie = movies.loc[movies['id'] == neighbor[0]]
        if(count < 5):
            avgRating = avgRating + (neighborMovie['vote_average'].values[0])*1.25
        else:
            avgRating = avgRating + (neighborMovie['vote_average'].values[0])*0.75
        count += 1
        allSimilar += str(neighborMovie['original_title'].values[0])+" | Rating: "+str(neighborMovie['vote_average'].values[0]) + "\n"
    avgRating = avgRating/K
    avgRating = round(avgRating, 2)
    
    return (allSimilar, avgRating, new_movie["original_title"].values[0], new_movie['vote_average'].values[0])

#method to run whats_my_score
def run(movie_to_search):
    api_key = 'api_key=27989ba887194f26874a5e95813460ab'
    api_search = 'https://api.themoviedb.org/3/search/movie?'
    api_movie = 'https://api.themoviedb.org/3/movie/'
    search_url = api_search + api_key + "&language=en-US&query=" + movie_to_search+ "&page=1&include_adult=false"
    search_response = requests.get(search_url)

    if(search_response.json()["total_results"] == 0):
        print("Could not find movie: " + movie_to_search)
        return (movie_to_search + " does not exist", 0, movie_to_search, 0)

    movie_id = search_response.json()["results"][0]["id"]
    movie_url = api_movie + str(movie_id) + "?" + api_key + "&language=en-US"
    credit_url = api_movie + str(movie_id) + "/credits?" + api_key + "&language=en-US"
    movie_response = requests.get(movie_url)
    credit_response = requests.get(credit_url)
    keywords_url = api_movie + str(movie_id) + "/keywords?" + api_key + "&language=en-US"
    keywords_response = requests.get(keywords_url)

    print(ctime(time()))
    add_raw_data(movie_response.json(), credit_response.json(), keywords_response.json())
    print(ctime(time()))
    add_clean_data(movie_response.json(), credit_response.json(), keywords_response.json())
    print(ctime(time()))
    movies = configure_movie_data()
    print(ctime(time()))
    res = whats_my_score(movie_id, movies)
    print(ctime(time()))
    return res