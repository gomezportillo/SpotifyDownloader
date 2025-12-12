import os
import json
import subprocess

from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

INPUT_FILE = "in/playlists.txt"
OUTPUT_ROOT = Path("out/Playlists")

# Spotify API credentials
with open("creds/spotify_credentials.json", "r") as f:
    creds = json.load(f)

SPOTIFY_CLIENT_ID = creds["client_id"]
SPOTIFY_CLIENT_SECRET = creds["client_secret"]

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

def read_playlists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_playlist_name(sp, playlist_url):
    playlist = sp.playlist(playlist_url)
    return playlist["name"]


def download_playlist(playlist_url, playlist_name):
    playlist_dir = OUTPUT_ROOT / playlist_name
    playlist_dir.mkdir(parents=True, exist_ok=True)

    print(f"Descargando '{playlist_name}' en {playlist_dir}")

    subprocess.run([
        "spotdl",
        "--output", str(playlist_dir),
        playlist_url,
        "--client-id", SPOTIFY_CLIENT_ID,
        "--client-secret", SPOTIFY_CLIENT_SECRET,
        "--threads", "6",
        "--overwrite", "skip",
        "--print-errors",
    ], check=True)


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: No existe el archivo {INPUT_FILE}")
        return

    urls = read_playlists(INPUT_FILE)

    if not urls:
        print("El archivo no contiene URLs.")
        return

    for url in urls:
        try:
            print(f"\nProcesando playlist: {url}")
            name = get_playlist_name(sp, url)
            download_playlist(url, name)

        except Exception as e:
            print(f"ERROR procesando {url}: {e}")


if __name__ == "__main__":
    main()
