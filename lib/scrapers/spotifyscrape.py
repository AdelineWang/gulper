from tornado import gen

import spotipy
from spotipy import oauth2

from lib.config import CONFIG
from .lib.basescraper import BaseScraper


class SpotifyScraper(BaseScraper):
    name = 'spotify'

    @property
    def num_songs(self, user_data):
        if CONFIG['_mode'] == 'prod':
            return 1000
        return 100

    @gen.coroutine
    def spot_track_paginate(self, client, req):
        tracks = []
        offset = 20
        while req['next'] is not None and offset < self.num_songs:
            for track in req['items']:
                song = {}
                song['name'] = track['name']
                song['id'] = track['id']
                song['artists'] = [ist['name'] for ist in track['artists']]
                song['album'] = track['album']['name']
                tracks.append(song)

            offset += 20
            req = client.current_user_saved_tracks(offset=offset)

        return tracks

    @gen.coroutine
    def spot_playlist_paginate(self, client, req, user_id):
        lists = []
        offset = 20
        while req['next'] is not None:
            for pls in req['items']:
                pl = {}
                pl['name'] = req['name']
                pl['id'] = req['id']
                pl['track_num'] = req['tracks']['total']
                pl['owner'] = req['owner']['id']
                lists.append(pls)

            offset += 20
            req = client.current_user_playlists(user_id=user_id, offset=offset)

        return lists

    @gen.coroutine
    def scrape(self, user_data):
        try:
            oauth = user_data.services['spotify']['access_token']
            refresh = user_data.services['spotify']['refresh_token']
        except KeyError:
            return False

        # Before authentication, refresh the token
        oauth2.SpotifyOAuth._refresh_access_token(self, refresh)
        spot = spotipy.Spotify(auth=oauth)

        spot_data = {}

        profile = spot.current_user()
        user_id = profile['id']

        playlists = spot.user_playlists(user=user_id)
        user_lists = yield [self.spot_playlist_paginate(spot, playlists)]
        spot_data['playlists'] = user_lists

        #Get individual playlist by id (Don't think we need)
        #sp.user_playlist(user=user_id, playlist=playlist_id)

        artists = spot.current_user_followed_artists()
        fav_artists = []
        #Could use low popularity to identify a potentially niche interest
        for art in artists:
            groupie = {}
            groupie['id'] = art['id']
            groupie['name'] = art['name']
            groupie['popularity'] = art['popularity']
            fav_artists.append(groupie)

        spot_data['artists'] = fav_artists
        tracks = spot.current_user_saved_tracks()
        fav_tracks = yield [self.spot_track_paginate(tracks)]

        spot_data['tracks'] = fav_tracks

        return spot_data
