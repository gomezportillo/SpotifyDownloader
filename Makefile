PYTHON = python3
PIP = pip3

all: download-songs

get-artists:
	$(PYTHON) src/get_my_artists.py

download-songs: get-artists
	$(PYTHON) src/download_spotify_artists.py in/followed_artists.txt

install:
	$(PIP) install --upgrade spotdl spotipy
