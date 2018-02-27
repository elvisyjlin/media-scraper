#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import json
import os
import sys
import time
import re
from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm
from util import seleniumdriver
from util.file import get_extension, rename_file, safe_makedirs
from util.instagram import parse_node
from util.url import get_filename, complete_url, download, is_media

class Scraper(metaclass=ABCMeta):

    def __init__(self, scroll_pause = 0.5, mode='normal', debug=False):
        self._scroll_pause_time = scroll_pause
        self._login_pause_time = 5.0
        self._mode = mode
        self._debug = debug

        if self._mode == 'verbose':
            print('Starting PhantomJS web driver...')
        self._driver = seleniumdriver.get('PhantomJS')

        # if self._mode == 'verbose':
        #     print('Starting Chrome web driver...')
        # self._driver = seleniumdriver.get('Chrome')

    def connect(self, url):
        if self._debug:
            print('Connecting to "{}"...'.format(url))
        self._driver.get(url)

    def source(self):
        return self._driver.page_source

    def print(self):
        print(self.source())

    def save(self, file):
        with open(file, 'wb') as f:
            f.write(self.source().encode('utf-8'))
        print('Saved web page to {}.'.format(file))

    def load_credentials(self, credentials_file):
        assert os.path.exists(credentials_file), 'Error: Credentials file "{}" does not exist.'.format(credentials_file)

        with open(credentials_file, 'r') as f:
            credentials = json.loads(f.read())

        if self._mode == 'verbose':
            print('Logging in as "{}"...'.format(credentials['username']))

        return credentials

    def find_element_by_class_name(self, class_name):
        try:
            element = self._driver.find_element_by_class_name(class_name)
            return element
        except:
            return None

    def scrollToBottom(self, fn=None, times=-1):
        if times < 0: times = sys.maxsize
        last_height, new_height = self._driver.execute_script("return document.body.scrollHeight"), 0
        counter = 0
        while (new_height != last_height or fn is not None and fn()) and counter < times:
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(self._scroll_pause_time)
            last_height = new_height
            new_height = self._driver.execute_script("return document.body.scrollHeight")
            counter += 1
        return not (new_height != last_height or fn is not None and fn())

    @abstractmethod
    def scrape(self):
        return None

    def download(self, tasks, path='.', force=False):
        if self._mode != 'silent':
            print('Downloading...')
        for url, rename in tqdm(tasks):
            download(url, path=path, rename=rename, replace=force)

    @abstractmethod
    def login(self):
        pass

class MediaScraper(Scraper):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.abs_url_regex = '([a-z0-9]*:|.{0})\/\/[^"\s]+'
        # self.rel_url_regex = '\"[^\/]+\/[^\/].*$|^\/[^\/].*\"'
        # self.abs_url_regex = '/^([a-z0-9]*:|.{0})\/\/.*$/gmi'
        # self.rel_url_regex = '/^[^\/]+\/[^\/].*$|^\/[^\/].*$/gmi'

    def scrape(self):
        self.scrollToBottom()

        if self._debug:
            self.save('test.html')

        source = self.source()

        # Parse links, images, and videos successively by BeautifulSoup parser.

        media_urls = [] 
        soup = BeautifulSoup(source, 'lxml')
        for link in soup.find_all('a', href=True):
            if is_media(link['href']):
                media_urls.append(link['href'])
            if is_media(link.text):
                media_urls.append(link.text)
        for image in soup.find_all('img', src=True):
            if is_media(image['src']):
                media_urls.append(image['src'])
        for video in soup.find_all('video', src=True):
            if is_media(video['src']):
                media_urls.append(video['src'])

        if self._debug:
            print(media_urls)

        tasks = [(complete_url(media_url, self._driver.current_url), None) for media_url in media_urls]

        if self._debug:
            print(tasks)

        if self._mode != 'silent':
            print('{} media are found.'.format(len(media_urls)))

        return tasks


        # # Parse links, images, and videos successively by native regex matching.

        # urls = re.findall('http', source)
        # print('test urls:')
        # for url in urls:
        #     print(url)

        # urls = re.findall(self.abs_url_regex, source)
        # print('abs urls:')
        # for url in urls:
        #     print(url)

        # urls = re.findall(self.rel_url_regex, source)
        # print('rel urls:')
        # for url in urls:
        #     print(url)

    def login(self, credentials_file):
        pass


class InstagramScraper(Scraper):

    # NOTES: 
    # 1. Naming rule of Instagram username: 
    #    (1) letters    (a-zA-Z) 
    #    (2) digits     (0-9) 
    #    (3) underline  (_) 
    #    (4) dot        (.) 
    # 2. Shortcode: 
    #    a string of 11 characters 
    # 3. In a page, there are at most 30 rows of posts.
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://www.instagram.com'
        self.login_url = 'https://www.instagram.com/accounts/login/'
        self.post_regex = '/p/[ -~]{11}/'

    def sharedData(self):
        return self._driver.execute_script("return window._sharedData")

    def username(self, username):
        self.connect('{}/{}/'.format(self.base_url, username))

    def scrape(self):
        if self._mode != 'silent':
            print('Crawling...')
        done = False
        codes = re.findall(self.post_regex, self.source())
        while not done:
            done = self.scrollToBottom(fn=lambda: self.find_element_by_class_name('_o5uzb'), times=3)
            codes += re.findall(self.post_regex, self.source())
        codes = list(set(codes))
        codes = [code[3:-1] for code in codes]

        if self._mode != 'silent':
            print('{} posts are found.'.format(len(codes)))

        if self._debug:
            self.save('test.html')
            with open('shortcodes.txt', 'w') as f:
                f.write(json.dumps(codes))

        if self._mode != 'silent':
            print('Scraping...')

        tasks = []
        for code in tqdm(codes):
            self.connect('{}/p/{}/'.format(self.base_url, code))
            data = self.sharedData()
            node = data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
            tasks += parse_node(node, node['owner']['username'])

        if self._mode != 'silent':
            print('{} media are found.'.format(len(tasks)))

        return tasks

    def scrapeSharedData(self):
        sharedData = self.sharedData()
        profilePage = sharedData['entry_data']['ProfilePage']
        print('# of profilePage: {}.'.format(len(profilePage)))
        user = profilePage[0]['user']
        print('# of following: {}.'.format(user['follows']['count']))
        print('Url of profile picture: {}.'.format(user['profile_pic_url_hd']))
        print('Full name: {}.'.format(user['full_name']))
        print('# of followers: {}.'.format(user['followed_by']))
        # user['media_collections']
        media = user['media']
        print('# of media: {}.'.format(media['count']))
        nodes = media['nodes']
        target = []
        for node in nodes:
            # node['date']
            # node['comments']['count']
            # node['is_video']
            # node['id']
            # node['__typename']
            target.append(node['code'])
            # node['likes']['count']
            # node['caption']
        # user['is_private']
        # user['username']

        with open('json.txt', 'w') as f:
            f.write(json.dumps(sharedData))

        with open('ids_shared_data.txt', 'w') as f:
            f.write(json.dumps(target))

    def login(self, credentials_file):
        credentials = self.load_credentials(credentials_file)

        self.connect(self.login_url)
        time.sleep(self._login_pause_time)

        username, password = self._driver.find_elements_by_tag_name('input')
        button = self._driver.find_element_by_tag_name('button')

        username.send_keys(credentials['username'])
        password.send_keys(credentials['password'])
        button.click()
        time.sleep(self._login_pause_time)


class TwitterScraper(Scraper):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://twitter.com'
        self.login_url = 'https://twitter.com/login'
        # self.post_regex = '/p/[ -~]{11}/'

    def username(self, username):
        self.connect('{}/{}/media'.format(self.base_url, username))

    def scrape(self):
        if self._mode != 'silent':
            print('Crawling...')

        done = self.scrollToBottom()

        source = self.source()
        soup = BeautifulSoup(source, 'lxml')

        # title = soup.find('title')
        # name = title.get_text().replace('Media Tweets by ', '').replace(' | Twitter', '')

        # avatar_url = soup.find("a", { "class" : "ProfileCardMini-avatar" }).get('data-resolved-url-large')
        # background_url = soup.find("div", { "class" : "ProfileCanopy-headerBg" }).find('img').get('src')

        tasks = []
        for div in soup.find_all('div', { "class" : "AdaptiveMedia-photoContainer" }):
            url = div.get('data-image-url')
            tasks.append((url+':large', get_filename(url)))

        if self._mode != 'silent':
            print('{} media are found.'.format(len(tasks)))

        return tasks

    def login(self, credentials_file):
        credentials = self.load_credentials(credentials_file)

        self.connect(self.login_url)
        time.sleep(self._login_pause_time)

        username = self._driver.find_element_by_name('session[username_or_email]')
        password = self._driver.find_element_by_name('session[password]')
        buttons = self._driver.find_elements_by_tag_name('button')
        button = [b for b in buttons if b.text != ''][0]

        username.send_keys(credentials['username'])
        password.send_keys(credentials['password'])
        button.click()
        time.sleep(self._login_pause_time)
