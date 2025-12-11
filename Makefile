VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

.PHONY: all activate install get-artist download-songs

all: install download-songs

# Crear entorno virtual
$(VENV_DIR)/bin/activate:
	python3 -m venv $(VENV_DIR)

activate:
	@echo "Run 'source $(VENV_DIR)/bin/activate' in your shell to activate the environment"

install: $(VENV_DIR)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade spotdl spotipy

get-artists: $(VENV_DIR)/bin/activate
	$(PYTHON) src/get_my_artists.py

download-songs: get-artists
	$(PYTHON) src/download_spotify_artists.py in/followed_artists.txt

# Limpiar archivos generados
clean:
	rm -fr $(VENV_DIR)
	rm -fr in/
