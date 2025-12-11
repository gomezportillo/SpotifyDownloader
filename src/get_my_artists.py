import os
import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth

# Spotify API credentials
with open("creds/spotify_credentials.json", "r") as f:
    creds = json.load(f)

SPOTIFY_CLIENT_ID = creds["client_id"]
SPOTIFY_CLIENT_SECRET = creds["client_secret"]

SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-follow-read"
))


def get_followed_artists_with_urls():
    """Obtiene la lista de artistas seguidos junto con sus URLs."""
    results = sp.current_user_followed_artists(limit=50) # number of artists per page
    artists_urls = []
    while results:
        for artist in results["artists"]["items"]:
            artist_name = artist["name"]
            artist_url = artist["external_urls"]["spotify"]
            artists_urls.append((artist_name, artist_url))
        results = sp.next(results["artists"])  # Paginación
    return artists_urls


def save_artists_to_file(artists, file_name):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    # Sort artists alphabetically by their name (case-insensitive)
    sorted_artists = sorted(artists, key=lambda x: x[0].lower())

    with open(file_name, "w") as f:
        for artist_name, artist_url in sorted_artists:
            f.write(f"{artist_name}:{artist_url}\n")

    print(f"Saved {len(sorted_artists)} artists to {file_name}.")


def main():
    print("Fetching followed artists with URLs...")

    artists_with_urls = get_followed_artists_with_urls()

    save_artists_to_file(artists_with_urls, "in/followed_artists.txt")


if __name__ == "__main__":
    main()
