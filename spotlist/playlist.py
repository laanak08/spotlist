from datetime import datetime

import dask
import spotipy.util

from spotlist.track import read_tracklist, tracks_from_list
from spotlist.util import server, prompt_for_user_token

dask.config.set(scheduler='threads')


def create(name: str, tracklist: str, **kwargs: str) -> None:
    with server():
        scope = "playlist-modify-public"
        token = prompt_for_user_token('spotlist-user', scope)

        if token:
            sp = spotipy.Spotify(auth=token)
            sp.trace_out = sp.trace = False

            print('Fetching user details')
            user_details = sp._get("me")
            user = user_details['id']

            print('building tracklist')
            raw_tracklist = read_tracklist(tracklist)
            tracks = tracks_from_list(sp, raw_tracklist)

            print('creating playlist')
            playlist = sp.user_playlist_create(user, name, description=f'SpotList: {datetime.now().date()}')

            print('adding tracks to playlist')
            sp.user_playlist_add_tracks(user, playlist['id'], [t['id'] for t in tracks])
            print(f'Playlist link: {playlist["external_urls"]["spotify"]}')
