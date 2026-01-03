# Anison

## Setup (Windows)

```bat
cd C:\music_library\music-collection
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
py -m mkdocs serve
