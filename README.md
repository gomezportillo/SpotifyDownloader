## Spotify downloader 💽

Tool for downloading full albums from Spotify using `spotdl`,

`spotipy` uses Spotify for downloading the artists metadata, and then `SpotDL` uses youtube-music to download the songs.

### How to use

* Install dependencies with `make install` or alternatively:
  * `spotDL` from https://github.com/spotDL/spotify-downloader
  * `spotipy` with `pip install spotipy`
* Create app in https://developer.spotify.com/dashboard and copy credentials in [creds/spotify_credentials.json](https://github.com/gomezportillo/SpotifyDownloader/tree/main/creds/spotify_credentials.json)
* Execute scripts with `make`

Alternatively, you can execute them individually using:

```sh
python3 src/get_my_artists.py
python3 src/download_discographies.py in/followed_artists.txt
python3 src/download_playlists.py in/playlists.txt
```
