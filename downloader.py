import configparser
import os
import urllib.parse
import urllib.request
import sys
from bs4 import BeautifulSoup
from os.path import basename
from tkinter import *
from tkinter import filedialog
from tqdm import tqdm

config = configparser.ConfigParser()
config.read('config.ini')

"""
root = Tk()
root.withdraw()
folder_selected = filedialog.askdirectory()

print(folder_selected)"""

BASE_URL = 'https://downloads.khinsider.com'
INPUT_FILE_NAME = 'input.txt'


class DownloadProgressBar(tqdm):
	def update_to(self, b=1, bsize=1, tsize=None):
		if tsize is not None:
			self.total = tsize
		self.update(b * bsize - self.n)


def download_url(url, output_path, file_name):
	with DownloadProgressBar(unit='B', unit_scale=True,
							 miniters=1, desc=file_name) as t:
		urllib.request.urlretrieve(
			url, filename=output_path, reporthook=t.update_to)


def validate_url(url):
	if '//downloads.khinsider.com/game-soundtracks/album/' not in url:
		return False
	return True


def find_images(soup, title):
	print('[info] Crawling for images...')

	imgs = soup.find_all('a')

	filtered_imgs = [img for img in imgs if img.get(
		"href") is not None and title in img.get("href") and 'jpg' in img.get("href")]

	if len(filtered_imgs) == 0:
		print('[error] No images found.')
		print('[error] url: ' + url)
		return False

	print('[info] ' + str(len(filtered_imgs)) + ' image/s acquired')
	return filtered_imgs


def find_songs(soup, title):
	song_list = soup.find(id="songlist")
	anchors = song_list.find_all('a')

	# href (string) -> song name (string)
	songMap = {}

	# Acquire links
	for anchor in anchors:
		href = anchor.get('href')
		if href and 'mp3' in href:
			href = BASE_URL + href
			if href not in songMap:
				songMap[href] = anchor.string
	if not songMap:
		print('[error] No songs found.')
		return False

	print('[info] ' + str(len(songMap)) + ' song links acquired')
	return songMap


def handle_download(file_url, dir_name, file_name):
	_file = urllib.request.urlopen(file_url)

	# Get file size
	meta = _file.info()
	file_size = float(meta.get("Content-Length")) / 1000000

	file_on_disk_path = dir_name + '/' + file_name

	# Check if file exists
	file_already_downloaded = False
	if os.path.exists(file_on_disk_path):
		stat = os.stat(file_on_disk_path)
		file_already_downloaded = round(
			float(stat.st_size) / 1000000, 2) == round(file_size, 2)

	# File exists but is not the same size
	if not file_already_downloaded:
		print('[downloading] ' + file_name +
			  ' [%.2f' % file_size + 'MB]')
		download_url(file_url, file_on_disk_path, file_name)
		print('[done] ' + file_name + '\n')
	else:
		print('[skipping] ' + file_name + ' already downloaded.')


def download_files(filetype, links, dir_name):
	downloaded_files = {}
	if filetype in ('hq', 'mp3'):
		print('[info] Downloading ' + filetype)
		songMap = links
		for song in songMap:
			link_soup = BeautifulSoup(
				urllib.request.urlopen(song), features="html.parser")
			song_urls = link_soup.select('a > span.songDownloadLink')
			for song_url in song_urls:
				song_url = song_url.parent.get('href')
				song_filetype = song_url.split('.')[-1]
				print(filetype,song_filetype)
				if filetype == 'mp3' and song_filetype != 'mp3':
					continue
				if filetype == 'hq' and song_filetype == 'mp3':
					continue			
				if song_url not in downloaded_files:
					downloaded_files[song_url] = True
					file_name = urllib.parse.unquote(basename(song_url))
					handle_download(song_url, dir_name, file_name)
	if filetype == 'jpg':
		images = links
		print('[info] Downloading ' + filetype)
		for img in images:
			img_url = img.get('href')
			if img_url not in downloaded_files:
				downloaded_files[img_url] = True
				file_name = basename(img_url)
				handle_download(img_url, dir_name, file_name)


def fetch_from_url(url):
	valid = validate_url(url)
	if not valid:
		print('[error] Invalid URL: ' + url)
		return
	print('[info] URL found: ' + url)

	base_dir = config["general"]["downloadlocation"]
	url_parts = url.split('/')

	title = url_parts[len(url_parts) - 1]
	dir_name = base_dir + '/' + title

	# Create directories
	if not os.path.exists(base_dir):
		print('[info] Creating directory: ' + base_dir)
		os.makedirs(base_dir)
	if not os.path.exists(dir_name):
		print('[info] Creating directory: ' + dir_name)
		os.makedirs(dir_name)

	print('[info] Crawling for links...')

	soup = BeautifulSoup(urllib.request.urlopen(
		url), features="html.parser", from_encoding="utf-8")
		
	mp3_only = False
	for mass_download_link in soup.select('div.albumMassDownload > div > a'):
		text = mass_download_link.text
		if text=='click to download':
			mp3_only = True
			print('[info] only mp3 is available')

	if config["general"].getboolean("images"):
		images = find_images(soup, title)
		if images == False:
			print('[info] no images available')
		else:
			download_files('jpg', images, dir_name)

	songMap = find_songs(soup, title)
	if config["general"].getboolean("hq") and mp3_only == False:
		download_files('hq', songMap, dir_name)
	else:
		download_files('mp3', songMap, dir_name)


def configure_settings():
	pass


try:
	if len(sys.argv) > 1:
		url = sys.argv[1]
		print('[info] Commandline argument found. Parsing links...')
		fetch_from_url(url)
	elif os.path.exists(INPUT_FILE_NAME):
		print('[info] Input file found. Parsing links...')
		input_file = open(INPUT_FILE_NAME, 'r')
		for line in input_file:
			fetch_from_url(line)
	else:
		print("[error] No argument passed and no input file found.")
except Exception as e:
	print("[error] " + str(e))
