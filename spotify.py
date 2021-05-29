import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import spotipy.oauth2 as oauth2
import warnings
from unidecode import unidecode
from time import sleep
from spotipy.exceptions import SpotifyException
import pickle

warnings.filterwarnings("ignore")

redirect_uri = "localhost:/callback"
client_secret = ""
client_id = ""
username = ""
# cache_path=".cache-"+username
scope = "playlist-modify-public playlist-modify-private"
time_to_wait_in_seconds = 60

url = input("url: ")
playlist_id = input("playlist id: ")

# token = util.prompt_for_user_token(
# username=username,
# ,
# client_id=client_id,
# client_secret=client_secret,
# redirect_uri=redirect_uri,
#

# token = util.prompt_for_user_token(username= username,
# scope = scope,
# client_id=client_id,
# client_secret=client_secret,
# redirect_uri=redirect_uri)
spotify = spotipy.Spotify(
    oauth_manager=spotipy.SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri,
                                       scope=scope, username=username))


# spotify = spotipy.Spotify(auth=token)
def save_song_list(song_list):
    with open(r'song_list.txt', 'wb') as fp:
        pickle.dump(song_list, fp)


def load_song_list():
    with open(r'song_list.txt', 'rb') as fp:
        itemlist = pickle.load(fp)
    return itemlist


while (True):
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    texts = [str.strip(x) for x in soup.strings if str.strip(x) != '']
    unwanted_text = [str.strip(x.text) for x in soup.find_all()]

    songs = list(set(texts).difference(unwanted_text))

    songs_dict = []

    for song in songs:
        song_name = song.split(", by ")[0].replace("[Radio Edit]", "").replace("[Radio Mix]", "").replace(
            "[Single Version]", "").replace("&", "And")
        song_author = song.split(", by ")[1]
        songs_dict.append({"name": song_name, "author": song_author})

    ids = []

    for song in songs_dict:
        result = spotify.search(song['name'] + " " + song['author'])

        flag = 1

        for item in result['tracks']['items']:
            if unidecode(item['artists'][0]['name']).replace("+", "And").replace("&", "And").lower().find(
                    song['author'].lower()) != -1 and unidecode(item['name']).replace("+", "And").replace("&",
                                                                                                       "And").lower().find(
                    song['name'].lower()) != -1:
                print(song['author'] + " " + song['name'] + " found")
                ids.append(item['id'])
                flag = 0
                break
        if flag:
            print(song['author'] + " " + song['name'] + " not found")

    songs_already_in_playlist = load_song_list()
    songs_to_add = list(set(ids).difference(songs_already_in_playlist))

    if songs_to_add:
        spotify.user_playlist_add_tracks(username, playlist_id, songs_to_add)

    save_song_list(songs_already_in_playlist + songs_to_add)

    sleep(time_to_wait_in_seconds)
