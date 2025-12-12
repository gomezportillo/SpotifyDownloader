import os
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

INPUT_FILE = "in/playlists.txt"
OUTPUT_ROOT = Path("out/Playlists")

MIN_DATE = None # datetime(2025, 1, 1, tzinfo=timezone.utc)

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


def get_tracks_after_date(sp, playlist_name, playlist_url, min_date):
    """Devuelve las URLs de canciones añadidas a partir de min_date."""

    print(f"Recuperando canciones de '{playlist_name}' añadidas desde {min_date.date()}...")

    tracks = []
    results = sp.playlist_items(playlist_url, additional_types=["track"], limit=100)

    while True:
        for item in results["items"]:
            added_at = item["added_at"]
            added_dt = datetime.fromisoformat(added_at.replace("Z", "+00:00"))

            if added_dt >= min_date:
                track = item["track"]
                if track:
                    tracks.append(track["external_urls"]["spotify"])

        if results["next"]:
            results = sp.next(results)
        else:
            break

    return tracks


def download_playlist_full(url, playlist_name):
    playlist_dir = OUTPUT_ROOT / playlist_name
    playlist_dir.mkdir(parents=True, exist_ok=True)

    print(f"Descargando playlist completa '{playlist_name} - {url}'...")

    cmd = [
        "spotdl",
        "--output", str(playlist_dir),
        url,
        "--client-id", SPOTIFY_CLIENT_ID,
        "--client-secret", SPOTIFY_CLIENT_SECRET,
        "--threads", "6",
        "--overwrite", "skip",
        "--print-errors",
    ]

    subprocess.run(cmd, check=True)


def download_tracks_individual(urls, playlist_name):
    playlist_dir = OUTPUT_ROOT / playlist_name
    playlist_dir.mkdir(parents=True, exist_ok=True)

    if not urls:
        print("No hay canciones que cumplan la fecha.")
        return

    print(f"Descargando {len(urls)} canciones...")

    cmd = [
        "spotdl",
        "download",
        *urls,
        "--output", str(playlist_dir),
        "--client-id", SPOTIFY_CLIENT_ID,
        "--client-secret", SPOTIFY_CLIENT_SECRET,
        "--threads", "6",
        "--overwrite", "skip",
        "--print-errors",
    ]

    subprocess.run(cmd, check=True)


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: No existe el archivo con playlists: {INPUT_FILE}")
        return

    urls = read_playlists(INPUT_FILE)

    if not urls:
        print("El archivo no contiene URLs.")
        return

    for url in urls:
        try:
            print(f"Procesando playlist: {url}")
            name = get_playlist_name(sp, url)

            if MIN_DATE is None:
                download_playlist_full(url, name)
            else:
                track_urls = get_tracks_after_date(sp, name, url, MIN_DATE)
                download_tracks_individual(track_urls, name)

        except Exception as e:
            print(f"ERROR procesando {url}: {e}")


if __name__ == "__main__":
    main()
