import functools
from pathlib import Path
from typing import List, Optional, Any

import dask.bag as db
import spotipy

from spotlist.util import remove_abbrevs, pipeline, remove_slashes

FOUND_TRACKS = set()


def read_tracklist(filepath: str) -> List[str]:
    file = str(Path(filepath).expanduser().resolve())
    with open(file) as fh:
        return [t.strip() for t in fh.readlines()]


def track_search(sp: spotipy.Spotify, query: str) -> Optional[Any]:
    try:
        results = sp.search(q=query, limit=5)
        if results and results['tracks'] and results['tracks']['items']:
            for item in results['tracks']['items']:
                if item['id'] not in FOUND_TRACKS:
                    FOUND_TRACKS.add(item['id'])
                    print(f'Search result: {item["name"]}, Query: {query}')
                    return item
    except:
        pass

    print(f'Search result: {None}, Query: {query}')
    return None


def tracks_from_list(sp: spotipy.Spotify, raw_tracklist: List[str]) -> List[Any]:
    tracklist_bag = db.from_sequence(raw_tracklist)

    cleaning_pipeline = (remove_abbrevs, remove_slashes)
    parallel_cleaning = functools.partial(pipeline, function_pipeline=cleaning_pipeline)
    parallel_track_search = functools.partial(track_search, sp)

    track_search_results = tracklist_bag.map(parallel_cleaning).map(parallel_track_search).compute()

    return [t for t in track_search_results if t]
