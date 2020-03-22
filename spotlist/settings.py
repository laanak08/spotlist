import os
from pathlib import Path
from typing import Optional, Dict, Tuple

SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''
SPOTIPY_REDIRECT_URI = ''

CACHE_FILE = str(Path('~/.spotlist_cache').expanduser().resolve())


def spotify_client_creds(client_id: Optional[str] = None,
                         client_secret: Optional[str] = None,
                         redirect_uri: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    Fetch or cache client credentials in home directory.

    Parameters
    ----------
    client_id : Spotify-provided client-id
    client_secret : Spotify-provided client-id

    Returns
    -------
    dict : str, str : client_id/client_secret
    """
    global CACHE_FILE

    cache_client_id_key = 'SPOTIPY_CLIENT_ID'
    cache_client_secret_key = 'SPOTIPY_CLIENT_SECRET'
    cache_client_redirect_uri = 'SPOTIPY_REDIRECT_URI'

    if client_id and client_secret:
        with open(CACHE_FILE, 'w') as fh:
            fh.write(f'{cache_client_id_key}={client_id}\n')
            fh.write(f'{cache_client_secret_key}={client_secret}\n')
            fh.write(f'{cache_client_redirect_uri}={redirect_uri}\n')
        return {
            cache_client_id_key: client_id,
            cache_client_secret_key: client_secret,
            cache_client_redirect_uri: redirect_uri
        }
    else:
        try:
            credentials: Dict[str, str] = {}
            with open(CACHE_FILE) as fh:
                for line in fh.readlines():
                    line = line.strip()
                    if line:
                        k, v = line.split('=')
                        credentials[k.upper()] = v

            if credentials:
                return credentials
        except FileNotFoundError:
            pass

    return None


def set_spotify_credentials() -> Tuple:
    """
    Read Spotify credential from cache/env and set CLIENT_ID/CLIENT_SECRET on os.environ

    Returns
    -------
    None
    """
    global SPOTIFY_CLIENT_ID
    global SPOTIFY_CLIENT_SECRET
    global SPOTIPY_REDIRECT_URI

    credentials = spotify_client_creds(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)
    if credentials:
        SPOTIFY_CLIENT_ID = credentials['SPOTIPY_CLIENT_ID']
        SPOTIFY_CLIENT_SECRET = credentials['SPOTIPY_CLIENT_SECRET']
        SPOTIPY_REDIRECT_URI = credentials['SPOTIPY_REDIRECT_URI']
    else:
        try:
            SPOTIFY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
            SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
            SPOTIPY_REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI')
            spotify_client_creds(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)
        except KeyError:
            raise Exception('Failed to locate SPOTIFY_CLIENT_ID and/or SPOTIFY_CLIENT_SECRET in env.')

    os.environ['SPOTIPY_CLIENT_ID'] = SPOTIFY_CLIENT_ID
    os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIFY_CLIENT_SECRET
    os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIPY_REDIRECT_URI

    return SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
