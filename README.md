# khdl

Script for downloading game soundtracks from [KHInsider](http://downloads.khinsider.com/).

## Usage
For downloading single albums:
```bash
./khdl <url> # If you downloaded an executable from releases
```
or
```bash
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
python downloader.py <url>
```
If downloading multiple albums, create an `input.txt` inside the current working directory, placing the albums' urls separated by a newline, and run the program without arguments.

## Configuration
Copy or rename `config.sample.ini` to `config.ini` in the current working directory and modify the parameters.
```dosini
[general]
; images (boolean): Whether to download images [True/False]
images = True
; hq (boolean): download other formats if available, e.g. FLAC, OGG
; will download mp3 if not available [True/False]
hq = True
; downloadlocation (string): relative or absolute path
downloadlocation = ./downloads
```
If no `config.ini` is found, images and mp3 are downloaded by default.

## Building
Standalone executables are built using [Nuitka](https://github.com/Nuitka/Nuitka).
```
pip install nuitka ordered-set zstandard
python -m nuitka --onefile downloader.py
```

## Notes
Just [donate](https://downloads.khinsider.com/forums/index.php?account/upgrades) to KHInsider if you can.