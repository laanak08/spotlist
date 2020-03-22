import re
import threading
import webbrowser
from contextlib import contextmanager
from functools import reduce
from typing import Sequence, Callable, TypeVar, Generator, Optional

import bottle
import spotipy

from spotlist.settings import set_spotify_credentials

T = TypeVar('T')
OAUTH_CODE_URL = ''

__all__ = ["CLIENT_CREDS_ENV_VARS", "prompt_for_user_token"]

CLIENT_CREDS_ENV_VARS = {
    "client_id": "SPOTIPY_CLIENT_ID",
    "client_secret": "SPOTIPY_CLIENT_SECRET",
    "client_username": "SPOTIPY_CLIENT_USERNAME",
    "redirect_uri": "SPOTIPY_REDIRECT_URI",
}


@bottle.route('/oauth_callback')
def oauth_callback() -> str:
    global OAUTH_CODE_URL
    OAUTH_CODE_URL = bottle.request.url
    return ""


@contextmanager
def server() -> Generator[None, None, None]:
    tid_server = threading.Thread(target=lambda: bottle.run(host='localhost', port=8080, debug=True))
    try:
        tid_server.start()
        yield
    finally:
        tid_server.join()


def prompt_for_user_token(username: str,
                          scope: str = None,
                          cache_path: str = None,
                          oauth_manager: spotipy.SpotifyOAuth = None,
                          show_dialog: bool = False) -> Optional[str]:
    """ prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify
        constructor

        Parameters:

         - username - the Spotify username
         - scope - the desired scope of the request
         - cache_path - path to location to save tokens
         - oauth_manager - Oauth manager object.

    """
    client_id, client_secret, redirect_uri = set_spotify_credentials()
    if not oauth_manager:
        if not client_id:
            print(
                """
                You need to set your Spotify API credentials.
                You can do this by setting environment variables like so:

                export SPOTIPY_CLIENT_ID='your-spotify-client-id'
                export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
                export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

                Get your credentials at
                    https://developer.spotify.com/my-applications
            """
            )
            raise spotipy.SpotifyException(550, -1, "no credentials set")

        cache_path = cache_path or ".cache-" + username

    sp_oauth = oauth_manager or spotipy.SpotifyOAuth(
        client_id, client_secret, redirect_uri, scope=scope, cache_path=cache_path, show_dialog=show_dialog
    )

    token_info = sp_oauth.get_cached_token()
    if token_info:
        return token_info["access_token"]

    auth_url = sp_oauth.get_authorize_url()
    try:
        # no cached token, send the user to a web page where they can authorize this app
        webbrowser.open(auth_url)
        print(f"Opened %s in your browser{auth_url}")
    except BaseException:
        print(f"Please navigate here: {auth_url}")

    while not OAUTH_CODE_URL:
        pass

    code = sp_oauth.parse_response_code(OAUTH_CODE_URL)
    token = sp_oauth.get_access_token(code, as_dict=False)

    return token if token else None


def pipeline(value: T, function_pipeline: Sequence[Callable[[T], T]]) -> T:
    """
    A generic Unix-like pipeline

    Parameters
    ----------
    value : the value you want to pass through a pipeline
    function_pipeline : an ordered list of functions that comprise your pipeline

    Returns
    -------
    T
    """
    try:
        return reduce(lambda v, f: f(v), function_pipeline, value)
    except:
        return value


def remove_abbrevs(s: str = '') -> str:
    return re.sub(r'\w{2}\.', '', s)


def remove_slashes(s: str = '') -> str:
    return re.sub(r'/', ' ', s)
