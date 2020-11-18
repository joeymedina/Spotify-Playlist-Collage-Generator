import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import collage_maker as cm
import os
import random
import shutil
import spotipy.util as util

#hello

class Album:
    def __init__(self, album_name, album_artist, uri, img_url):
        self.album_name = album_name
        self.album_artist = album_artist
        self.uri = uri
        self.img_url = img_url
    
    def toString(self):
        return self.album_name + ' - ' + self.album_artist 

class SpotAPI:
        
    def download_album_img(self, url, outputname, base_address):
        img_data = requests.get(url).content
        address =  base_address + outputname + '.jpg'

        with open(address, 'wb') as handler:
            handler.write(img_data)

    #begin image download
    def download_images(self, playlist, albums_list, base_address):
        print('Downloading images...')
        for i in range(len(playlist)):
            if playlist[i].album_name in albums_list: 
                self.download_album_img(playlist[i].img_url, str(i), base_address)
                albums_list.remove(playlist[i].album_name)
    #end image download

    def find_user_playlists(self, sp):
        print('Here are you Spotify Playlists:')
        print('-------------------------------')
        results = sp.current_user_playlists(limit=50)
        for i, item in enumerate(results['items']):
            print("%d %s" % (i, item['name']))
        return results

    #begin make collage
    def make_album_collage(self, base_address, playlist_name):
        print('Making album collage...')
        files = [os.path.join(base_address, fn) for fn in os.listdir(base_address)]
        images = [fn for fn in files if os.path.splitext(fn)[1].lower() in ('.jpg', '.jpeg', '.png')]
        random.shuffle(images)
        cm.make_collage(images, 'C:\\Users\\Joey\\Desktop\\{}.jpg'.format(playlist_name), 7000, 640)
        shutil.rmtree(base_address)
        print('Collage complete! Check C:\\Users\\Joey\\Desktop\\{}.jpg'.format(playlist_name))
    #end make collage

    #begin making list of playlist items
    def populate_playlist(self, tracks, playlist, album_list_with_duplicates, sp):
        print('Populating tracks...')
        for i, t in enumerate(tracks['items']):
                x = Album(t['track']['album']['name'], t['track']['artists'][0]['name'],t['track']['uri'],t['track']['album']['images'][0]['url'])
                y = t['track']['album']['name']
                playlist.append(x)
                album_list_with_duplicates.append(y)

        while tracks['next']:
            tracks = sp.next(tracks)
            for i, t in enumerate(tracks['items']):
                x = Album(t['track']['album']['name'], t['track']['artists'][0]['name'],t['track']['uri'],t['track']['album']['images'][0]['url'])
                y = t['track']['album']['name']
                playlist.append(x)
                album_list_with_duplicates.append(y)
    #end making list of playlist items

    #begin selecting your playlist
    def select_playlist(self,playlist):
        print('\nSelect the playlist you would like to create a collage for: (0-49)')
        selection = int(input())
        pl_selection = playlist['items'][selection]['uri']
        return pl_selection
    #end selecting your playlist

def main():

    #auth_manager = SpotifyClientCredentials(client_secret= "14fd1f993ca34e00b6b28233ef3b71aa", client_id="c1b2e5c1f56a45c38ce8b680ab6e643e")
    #sp = spotipy.Spotify(auth_manager=auth_manager)

    token = util.prompt_for_user_token(
             '1242158203', 
             '', 
             client_id='c1b2e5c1f56a45c38ce8b680ab6e643e',
             client_secret='14fd1f993ca34e00b6b28233ef3b71aa', 
             redirect_uri='http://localhost:8888/callback')

    sa = SpotAPI() 
    sp = spotipy.Spotify(auth=token)

    allplaylists = sa.find_user_playlists(sp)
    pl_id = sa.select_playlist(allplaylists)
    
    playlist = []
    album_list_with_duplicates = []
    
    playlist_items = sp.playlist(pl_id, fields="tracks,next,name")
    playlist_name = playlist_items['name']
    base_address = 'C:\\Users\\Joey\\Desktop\\{}\\'.format(playlist_name)
    os.makedirs(base_address)

    tracks = playlist_items['tracks']

    sa.populate_playlist(tracks, playlist, album_list_with_duplicates, sp)
    albums_list = list(set(album_list_with_duplicates))
    sa.download_images(playlist, albums_list, base_address)
    sa.make_album_collage(base_address, playlist_name)

if __name__ == '__main__':
    main()

