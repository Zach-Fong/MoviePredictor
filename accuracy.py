from model import add_raw_data
from model import add_clean_data
from model import configure_movie_data
from model import whats_my_score
import pandas as pd
import requests

#finds the accuracy of the predicted score vs the actual score
def calculateAccuracy(movies):
    movie_ids = []
    for movie in movies:
        api_key = 'api_key=27989ba887194f26874a5e95813460ab'
        api_search = 'https://api.themoviedb.org/3/search/movie?'
        api_movie = 'https://api.themoviedb.org/3/movie/'
        search_url = api_search + api_key + "&language=en-US&query=" + movie + "&page=1&include_adult=false"
        search_response = requests.get(search_url)

        if(search_response.json()["total_results"] == 0):
            print("Could not find movie: " + movie)
            return False

        movie_id = search_response.json()["results"][0]["id"]
        movie_ids.append(movie_id)
        movie_url = api_movie + str(movie_id) + "?" + api_key + "&language=en-US"
        credit_url = api_movie + str(movie_id) + "/credits?" + api_key + "&language=en-US"
        movie_response = requests.get(movie_url)
        credit_response = requests.get(credit_url)
        keywords_url = api_movie + str(movie_id) + "/keywords?" + api_key + "&language=en-US"
        keywords_response = requests.get(keywords_url)

        add_raw_data(movie_response.json(), credit_response.json(), keywords_response.json())
        add_clean_data(movie_response.json(), credit_response.json(), keywords_response.json())
    
    configuredMovies = configure_movie_data()
    results = []
    for movie_id in movie_ids:
        print(movie_id)
        results.append(whats_my_score(movie_id, configuredMovies))
    
    sumPredicted = 0
    sumAverage = 0
    for cur in results:
        difPredicted = abs(cur[1] - cur[3])
        difAverage = abs(getAverageScore() - cur[3])
        sumPredicted += difPredicted
        sumAverage += difAverage
        print(cur[2] + " difference predicted: " + str(difPredicted) + " | " + "difference average: " + str(difAverage))
    print("Total difference predicted: " + str((sumPredicted*10)/len(movies)) + "%")
    print("Total difference average: " + str((sumAverage*10)/len(movies)) + "%")
    
def runAccuracy():
    moviesRandom1 = ["unlocked","troy","clerks","mission: impossible ii","new nightmare","saving mr. banks","the night comes for us",
    "the secret of kells","the kissing booth","the first beautiful thing","the fast and the furious","overboard","safety not guaranteed",
    "the darjeeling limited","the wind that shakes the barley","spontaneous","the polar express","i spit on your grave 2","W.","The Bone Collector",
    "Milk","Delicatessen","Cradle 2 the Grave","My Name Is Nobody","The Mule","Grave of the Fireflies","A Christmas Prince: The Royal Wedding",
    "The Indian in the Cupboard","Dheepan","How to Train Your Dragon 2","Mesrine: Public Enemy #1","Take the Money and Run","State of Play",
    "Deepwater Horizon","A Man Apart","The Drop","Moana","Loving","The Founder","Small Soldiers","Rendition","The Walk","The Kings of Summer",
    "The Jungle Book","Weekend","Phineas and Ferb the Movie: Across the 2nd Dimension","Sinister","I Feel Pretty","Strangers on a Train",
    "Just Go with It"]
    moviesRandom2 = ["Forrest Gump","Eternal Sunshine of the Spotless Mind","King Kong","Strange Days","The Lost World: Jurassic Park",
    "Cube Zero","Stranger Than Paradise","Wild at Heart","Contact","The Spy Who Loved Me","Face/Off","GoodFellas","Blue Velvet",
    "Moulin Rouge!","Duel","Close Encounters of the Third Kind","Strangers on a Train","Planet of the Apes","Cars","The Pink Panther",
    "Lethal Weapon 2","The French Connection","Point Break","The Dreamers","Frida","The Fountain","ParentHood","Ray","The Empire Strikes Back",
    "Vanilla Sky","Fantastic Four: Rise of the Silver Surfer","We Own the Night","Final Fantasy: The Spirits Within","Closer","Space Jam",
    "Saving Grace","Heathers","In the Mouth of Madness","Basic Instinct 2","Barry Lyndon","Mr. Brooks","No Reservations","The Lady From Shanghai",
    "Road to Perdition","Be Cool","Armored","Leatherheads","An American Tail","The Fugitive","Pee-wee's Big Adventure"]
    moviesPopular = ["Top Gun: Maverick","Nope","Bullet Train","Prey","Orphan: First Kill","Day Shift","Samaritan","Look Both Ways","Top Gun",
    "Elvis","The Gray Man","Thirteen Lives","Beast","365 Days","The Black Phone","Me Time","Dragon Ball Super: Super Hero",
    "Super Pets","Orphan","Where The Crawdads Sing","Thor: Love and Thunder","Three Thousand Years of Longing","The Invitation",
    "Everything Everywhere All at Once","Bodies Bodies Bodies","Purple Hearts","Jurassic World Dominion","Fall","Uncharted","X",
    "Vengeance","Lightyear","laal singh chaddha","The Batman","The Lost City","Licorice Pizza","The Northman","Spin me Round",
    "Spider-Man: No Way Home","The Godfather","Sing 2"]

    calculateAccuracy(moviesRandom1)
    print(len(moviesRandom1))

    calculateAccuracy(moviesRandom2)
    print(len(moviesRandom2))

    calculateAccuracy(moviesPopular)
    print(len(moviesPopular))

#finds what the average score is across the entire local movie database
def getAverageScore():
    dynamic=pd.read_csv('./data/tmdb_dynamic.csv')
    return dynamic.sum(axis=0,numeric_only=True)['vote_average'] / dynamic.shape[0]