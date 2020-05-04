# khinsider-mp3-downloader

A script to crawl `http://downloads.khinsider.com/` for game soundtracks and download them. Downloads will be placed inside a `/downloads` directory inside the repo. Individual directories for each album will be generated automatically off the url name.

## Install
1. Create a virtual environment and activate it.
2. Install requirements with `$ pip install -r requirements.txt`

## How To Use

### Input URL via argv

The downloader takes one argument from the commandline as the program is run, i.e. `$ python downloader.py url`

### `input.txt`

Update the `input.txt` in the repo with a list of links, one link per line, and then run the script `$ python downloader.py`.
The repo includes a properly formatted `input.txt` for reference.

### Configuration

Edit config.py to modify files to download. JPG, FLAC, and MP3 are available.