import os
import requests
from requests.exceptions import RequestException
from html.parser import HTMLParser
import random
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin



BASE_URLS = [
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Srimad_Bhagavatam/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Audio_Books/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Bhagavad_Gita/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Bhajans/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Brhad_Bhagavatmrita/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Chaitanya_Charitamrita/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Course/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Festivals/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Krishna_Book/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Nectar_of_Devotion/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Nectar_of_Instruction/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Question_and_Answer/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Ramayan/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Seminar/',
  'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/Various/',  
]

CACHE_FILE = 'cache/mp3_files_cache.json'
CACHE_DURATION = 7 * 24 * 60 * 60  # One week


class AnchorTagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    link = attr[1]
                    if link.endswith('.mp3') or link.endswith('/'):
                        self.links.append(link)


async def fetchPage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the response contains an HTTP error
        return response.text
    except RequestException as e:
        print(f"Error fetching page {url}: {e}")
        return ""

def parseHTML(base_url, html):
    parser = BeautifulSoup(html, 'html.parser')
    anchor_tags = parser.find_all('a')
    links = []

    for anchor_tag in anchor_tags:
        if anchor_tag.text == "Parent Directory":
            continue

        link = anchor_tag.get('href')
        if link.endswith('.mp3') or link.endswith('/') and link != 'https://audio.iskcondesiretree.com/02_-_ISKCON_Swamis/ISKCON_Swamis_-_A_to_C/His_Holiness_Bir_Krishna_Goswami/':
            print(link)
            # Use urljoin only when the link is relative
            if not link.startswith('http'):
                link = urljoin(base_url, link)
            links.append(urljoin(base_url, link))

    return links


async def crawlDirectory(base_url):
    html = await fetchPage(base_url)
    links = parseHTML(base_url, html)
    mp3_files = []
    subdirs = []

    for link in links:
        if link.endswith('.mp3'):
            print(f"Found file: {link}")
            mp3_files.append(link)
        else:
            subdirs.append(link)

    for subdir in subdirs:
        subdir_mp3_files = await crawlDirectory(subdir)
        mp3_files.extend(subdir_mp3_files)

    return mp3_files


def cache_files(files):
    expiration = time.time() + CACHE_DURATION if len(files) >= 500 else time.time() - 1
    data = {
        'files': files,
        'expiration': expiration,
    }

    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)


async def load_cached_files():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            if time.time() < data['expiration']:
                return data['files']

    all_files = []
    for base_url in BASE_URLS:
        files = await crawlDirectory(base_url)  # Fix the function name here
        all_files.extend(files)

    cache_files(all_files)
    return all_files


def get_all_files():
    files = load_cached_files()
    return files


def get_random_file():
    files = get_all_files()
    random_index = random.randint(0, len(files) - 1)
    return files[random_index]

