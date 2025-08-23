import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import os
import subprocess
import argparse
import time
import re

# Spotify API credentials
SPOTIFY_CLIENT_ID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
SPOTIFY_CLIENT_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

OUTPUT_FOLDER = "Artists"
MIN_YEAR = 1990

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))


def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '-', name)


def get_albums(artist_id):
    albums = []
    seen_album_ids = set()

    for album_group in ['album', 'single', 'compilation']:  # album, single, compilation, appears_on
        results = sp.artist_albums(artist_id, album_type=album_group)
        while results:
            for album in results['items']:

                if album['id'] not in seen_album_ids:
                    release_date = album['release_date']
                    release_year = int(release_date.split("-")[0])

                    if release_year >= MIN_YEAR:
                        seen_album_ids.add(album['id'])
                        albums.append(album)
                    else:
                        print(f"Ignoring {album_group} {album['name']}' released in {release_year}")

            results = sp.next(results)

    return albums


def get_tracks(album_id):
    album_tracks = []
    results = sp.album_tracks(album_id)
    while results:
        album_tracks.extend(results['items'])
        results = sp.next(results) if results['next'] else None
    return album_tracks


def download_album(album_url, output_folder):
    subprocess.run([
        "spotdl",
        album_url,
        "--output", output_folder
    ])


def rename_tracks(album_folder_path, tracks):
    """Rename the downloaded tracks in the album folder."""
    for index, track in enumerate(tracks, start=1):

        track_name = track['name']
        artist = track['artists'][0]['name']
        original_name = f"{artist} - {track_name}.mp3"

        original_file_path = os.path.join(album_folder_path, original_name)
        if os.path.exists(original_file_path):
            # Create the new file name
            new_name = f"{index:02d} - {track_name}.mp3"
            new_file_path = os.path.join(album_folder_path, new_name)

            # Rename the file
            os.rename(original_file_path, new_file_path)
            print(f"Renamed: {original_name} -> {new_name}")
        else:
            print(f"Can't rename, file {original_name} not found in folder {album_folder_path}")


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Download albums from Spotify artists.')
    parser.add_argument('artists_file', type=str, help='File with list of Spotify artist URLs')
    args = parser.parse_args()

    # Read artist URLs from file
    with open(args.artists_file, "r") as f:
        artist_urls = [
            line.split(":", 1)[1].strip() if ":" in line else line.strip()
            for line in f if line.strip()
        ]

    # Folder where songs will be saved
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for artist_url in artist_urls:
        try:
            # Extract artist ID from URL
            artist_id = artist_url.split("/")[-1].split("?")[0]
            artist_info = sp.artist(artist_id)
            artist_name = artist_info['name']

            print(f"Fetching albums for: {artist_name}")
            albums = get_albums(artist_id)

            for album in albums:
                album_name = sanitize_filename(album['name'])
                album_year = album['release_date'].split("-")[0]
                album_url = album['external_urls']['spotify']

                # Create folder path
                album_folder_name = f"{album_year} - {album_name}"
                album_folder_path = os.path.join(OUTPUT_FOLDER, artist_name, album_folder_name)
                os.makedirs(album_folder_path, exist_ok=True)

                print(f"Downloading album: {album_folder_name}")

                # Download album
                download_album(album_url, album_folder_path)

                # Get the tracks for the album
                tracks = get_tracks(album['id'])

                # Wait a little to ensure files are downloaded
                time.sleep(1)  # Adjust if necessary

                # Rename the songs according to track number and album year
                rename_tracks(album_folder_path, tracks)

        except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(f"Error processing {artist_url}: {e}")
                print(exc_type, fname, exc_tb.tb_lineno)


if __name__ == "__main__":
    main()
