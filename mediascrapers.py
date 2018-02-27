#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import json
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
        self._mode = mode
        self._debug = debug

        if self._mode == 'verbose':
            print('Starting PhantomJS web driver...')
        # self._driver = webdriver.PhantomJS()
        self._driver = seleniumdriver.get('PhantomJS')

    def connect(self, url):
        if self._mode == 'verbose':
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

    def find_element_by_class_name(self, class_name):
        try:
            element = self._driver.find_element_by_class_name(class_name)
            return element
        except:
            return None

    def scrollToBottom(self, fn=None):
        last_height, new_height = self._driver.execute_script("return document.body.scrollHeight"), 0
        while new_height != last_height or fn is not None and fn():
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(self._scroll_pause_time)
            last_height = new_height
            new_height = self._driver.execute_script("return document.body.scrollHeight")

    @abstractmethod
    def scrape(self, path='.'):
        pass

    @abstractmethod
    def login(self, username, password):
        pass

class MediaScraper(Scraper):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.abs_url_regex = '([a-z0-9]*:|.{0})\/\/[^"\s]+'
        # self.rel_url_regex = '\"[^\/]+\/[^\/].*$|^\/[^\/].*\"'
        # self.abs_url_regex = '/^([a-z0-9]*:|.{0})\/\/.*$/gmi'
        # self.rel_url_regex = '/^[^\/]+\/[^\/].*$|^\/[^\/].*$/gmi'

    def scrape(self, path='.'):
        self.scrollToBottom()

        if self._debug:
            self.save('test.html')

        source = self.source()

        # Parse links, images, and videos successively by BeautifulSoup parser.

        media_urls = [] 
        soup = BeautifulSoup(source, "lxml")
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

        media_urls = [complete_url(media_url, self._driver.current_url) for media_url in media_urls]

        if self._debug:
            print(media_urls)

        if self._mode != 'silent':
            print('{} media are found.'.format(len(media_urls)))

        for media_url in tqdm(media_urls):
            download(media_url, path=path)


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

    def login(self, username, password):
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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://www.instagram.com'
        self.post_regex = '/p/[ -~]{11}/'

    def sharedData(self):
        return self._driver.execute_script("return window._sharedData")

    def username(self, username):
        self.connect('{}/{}/'.format(self.base_url, username))

    def scrape(self, path='.'):
        self.scrollToBottom(fn=lambda: self.find_element_by_class_name('_o5uzb'))

        source = self.source()
        codes = re.findall(self.post_regex, source)
        codes = [code[3:-1] for code in codes]

        if self._debug:
            self.save('test.html')
            with open('shortcodes.txt', 'w') as f:
                f.write(json.dumps(codes))

        tasks = []
        for code in codes:
            self.connect('{}/p/{}/'.format(self.base_url, code))
            data = self.sharedData()
            node = data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
            tasks += parse_node(node, node['owner']['username'])

        if self._mode != 'silent':
            print('{} posts are found.'.format(len(codes)))
            print('{} media are found.'.format(len(tasks)))
            
        for url, rename in tqdm(tasks):
            download(url, path=path, rename=rename)

    def can_scroll(self):
        self._driver

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

    def login(self, username, password):
        pass
