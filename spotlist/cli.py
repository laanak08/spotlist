import argparse
import sys
from typing import Dict

import spotlist
import spotlist.playlist


def parse_args() -> Dict[str, str]:
    parser = argparse.ArgumentParser(description='Convert list to Spotify playlist.')
    subparsers = parser.add_subparsers(help='Operations')

    make_playlist_parser = subparsers.add_parser('make-playlist', help='convert csv to playlist.')
    make_playlist_parser.add_argument('-n', '--name', required=True, help='new playlist name.')
    make_playlist_parser.add_argument('-t', '--tracklist', required=True, help='path to csv.')
    make_playlist_parser.add_argument('-u', '--user', required=False, help='spotify username.')

    return vars(parser.parse_args())


def main() -> None:
    spotlist.playlist.create(**parse_args())
    sys.exit(0)


if __name__ == '__main__':
    main()
