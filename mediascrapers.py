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
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from tqdm import tqdm
from util import seleniumdriver
from util.file import get_basename, get_extension, rename_file, safe_makedirs
from util.instagram import parse_node
from util.twitter import get_twitter_video_url
from util.url import get_filename, complete_url, download, is_media

class Scraper(metaclass=ABCMeta):

    def __init__(self, driver='phantomjs', scroll_pause=1.0, next_page_pause=1.0, mode='normal', debug=False):
        self._scroll_pause_time = scroll_pause
        self._next_page_pause_time = next_page_pause
        self._login_pause_time = 5.0
        self._mode = mode
        self._debug = debug
        self._name = 'scraper'

        if self._debug:
            driver = 'chrome'

        if driver == 'phantomjs':
            if self._mode != 'silent':
                print('Starting PhantomJS web driver...')
            self._driver = seleniumdriver.get('PhantomJS')
        elif driver == 'chrome':
            if self._mode == 'verbose':
                print('Starting Chrome web driver...')
            self._driver = seleniumdriver.get('Chrome')
        else:
            raise Exception('Driver not found "{}".'.format(driver))
            
        # self._driver.set_window_size(1920, 1080)

    def _connect(self, url):
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

        assert self._name in credentials, 'Error: "{}" does not support credentials.'.format(self._name)

        credentials = credentials[self._name]
        if self._mode == 'verbose':
            user = credentials.keys().remove('password')
            print('Logging in as "{}"...'.format(credentials[user]))
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
        for url, folder, rename in tqdm(tasks):
            target_path = path
            if folder is not None:
                target_path = os.path.join(target_path, folder)
            download(url, path=target_path, rename=rename, replace=force)

    @abstractmethod
    def login(self):
        pass

class MediaScraper(Scraper):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name = 'general'
        # self.abs_url_regex = '([a-z0-9]*:|.{0})\/\/[^"\s]+'
        # self.rel_url_regex = '\"[^\/]+\/[^\/].*$|^\/[^\/].*\"'
        # self.abs_url_regex = '/^([a-z0-9]*:|.{0})\/\/.*$/gmi'
        # self.rel_url_regex = '/^[^\/]+\/[^\/].*$|^\/[^\/].*$/gmi'

    def scrape(self, url):
        self._connect(url)
        self.scrollToBottom()

        if self._debug:
            self.save('test.html')

        source = self.source()

        # Parse links, images, and videos successively by BeautifulSoup parser.

        media_urls = [] 
        soup = bs(source, 'html.parser')
        title = soup.find('title').text
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

        tasks = [(complete_url(media_url, self._driver.current_url), title, None) for media_url in media_urls]

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
    #    not necessarily is a string of 11 characters 
    #    maybe a string of 38 (on private account)
    # 3. In a page, there are at most 30 rows of posts.
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name = 'instagram'

        self.login_url = 'https://www.instagram.com/accounts/login/'
        self.json_data_url = 'https://www.instagram.com/{}/?__a=1'
        self.json_data_url_with_max_id = 'https://www.instagram.com/{}/?__a=1&max_id={}'
        self.new_json_data_url = 'https://www.instagram.com/graphql/query/?query_hash={}&variables={{"id":"{}","first":{},"after":"{}"}}'
        self.query_parameters = {
            'query_hash': '472f257a40c653c64c666ce877d59d2b', 
            'first': 12
        }
        self.post_regex = '\/p\/[^\/]+\/'

    # def getJsonData(self, target, max_id=None):
    #     if max_id is None:
    #         self._connect(self.json_data_url.format(target))
    #     else:
    #         self._connect(self.json_data_url_with_max_id.format(target, max_id))
    #     content = self._driver.find_element_by_tag_name('pre').text
    #     data = json.loads(content)
    #     return data

    def getJsonData(self, user_or_id, after=None):
        if after is None:   # user_or_id should be username
            self._connect(self.json_data_url.format(user_or_id))
        else:               # user_or_id should be id
            self._connect(self.new_json_data_url.format(
                self.query_parameters['query_hash'], user_or_id, self.query_parameters['first'], after))
        content = self._driver.find_element_by_tag_name('pre').text
        data = json.loads(content)
        return data

    def sharedData(self):
        return self._driver.execute_script("return window._sharedData")

    def scrape(self, username):
        if self._mode != 'silent':
            print('Crawling...')

        data = self.getJsonData(username)

        # user = data['user']
        # media = user['media']
        # nodes = media['nodes']

        user = data['graphql']['user']
        user_id = user['id']
        media = user['edge_owner_to_timeline_media']
        count = media['count']
        # print('Count: {}'.format(count))
        page_info = media['page_info']
        edges = media['edges']
        has_next_page = page_info['has_next_page']
        end_cursor = page_info['end_cursor']

        tasks = []
        num_post = 0
        while len(edges) > 0:
            num_post += len(edges)
            for edge in edges:
                # post = self.getJsonData('p/'+node['code'])
                post = self.getJsonData('p/'+edge['node']['shortcode'])
                task = parse_node(post['graphql']['shortcode_media'])
                tasks += (task[0], username, task[1])
            # nodes = data['user']['media']['nodes']
            if has_next_page:
                # data = self.getJsonData(username, edges[-1]['node']['id'])
                data = self.getJsonData(user_id, end_cursor)
                try:
                    edges = data['data']['user']['edge_owner_to_timeline_media']['edges']
                except Exception as e:
                    print(data)
                    print(e)
                has_next_page = data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
                end_cursor = data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            else:
                break

        if self._mode != 'silent':
            print('{} posts are found.'.format(num_post))

        if self._mode != 'silent':
            print('{} media are found.'.format(len(tasks)))

        return tasks

    def scrapePage(self, username):
        self._connect('{}/{}/'.format(self.base_url, username))

        if self._mode != 'silent':
            print('Crawling...')
        done = False
        codes = re.findall(self.post_regex, self.source())
        while not done:
            done = self.scrollToBottom(fn=lambda: self.find_element_by_class_name('_o5uzb'), times=2)
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
            self._connect('{}/p/{}/'.format(self.base_url, code))
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
        return
        
        if credentials['username'] == '' or credentials['password'] == '':
            print('Either username or password is empty. Abort login.')

        if self._mode != 'silent':
            print('Logging in as "{}"...'.format(credentials['username']))

        self._connect(self.login_url)
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
        self._name = 'twitter'

        self.base_url = 'https://twitter.com'
        self.login_url = 'https://twitter.com/login'
        # self.post_regex = '/p/[ -~]{11}/'
        self.scroll_pause = 3.0

    def scrape(self, username):
        self._connect('{}/{}/media'.format(self.base_url, username))

        if self._mode != 'silent':
            print('Crawling...')

        done = self.scrollToBottom()

        source = self.source()
        soup = bs(source, 'html.parser')

        # title = soup.find('title')
        # name = title.get_text().replace('Media Tweets by ', '').replace(' | Twitter', '')

        # avatar_url = soup.find("a", { "class" : "ProfileCardMini-avatar" }).get('data-resolved-url-large')
        # background_url = soup.find("div", { "class" : "ProfileCanopy-headerBg" }).find('img').get('src')

        tasks = []
        for li in soup.find_all('li', {'class': 'js-stream-item stream-item stream-item '}):
            photos = li.find_all('div', { "class" : "AdaptiveMedia-photoContainer" })
            if photos == []:
                try:
                    img_url, vid_url = get_twitter_video_url(li['data-item-id'])
                    tasks.append((img_url+':large', username, get_basename(get_filename(img_url))))
                    tasks.append((vid_url, username, get_basename(get_filename(vid_url))))
                except Exception as e:
                    with open('error.txt', 'w', encoding='utf-8') as f:
                        f.write(str(e) + '\n')
                        f.write(str(li))
            else:
                for photo in photos:
                    url = photo['data-image-url']
                    tasks.append((url+':large', username, get_basename(get_filename(url))))
        for div in soup.find_all('div', { "class" : "AdaptiveMedia-photoContainer" }):
            url = div['data-image-url']
            tasks.append((url+':large', username, get_basename(get_filename(url))))

        if self._mode != 'silent':
            print('{} media are found.'.format(len(tasks)))

        return tasks

    def login(self, credentials_file):
        credentials = self.load_credentials(credentials_file)
        
        if credentials['username'] == '' or credentials['password'] == '':
            print('Either username or password is empty. Abort login.')
            return

        if self._mode != 'silent':
            print('Logging in as "{}"...'.format(credentials['username']))

        self._connect(self.login_url)
        time.sleep(self._login_pause_time)

        usernames = self._driver.find_elements_by_name('session[username_or_email]')
        passwords = self._driver.find_elements_by_name('session[password]')
        buttons = self._driver.find_elements_by_tag_name('button')
        username = [u for u in usernames if u.get_attribute('class') == 'js-username-field email-input js-initial-focus'][0]
        password = [p for p in passwords if p.get_attribute('class') == 'js-password-field'][0]
        button = [b for b in buttons if b.text != ''][0]
        self._driver.save_screenshot('test.png')
        self._driver.implicitly_wait(10)

        username.send_keys(credentials['username'])
        password.send_keys(credentials['password'])
        button.click()
        time.sleep(self._login_pause_time)


class FacebookScraper(Scraper):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name = 'facebook'

        self.base_url = 'https://www.facebook.com'
        self.login_url = 'https://www.facebook.com/login'
        # self.post_regex = '/p/[ -~]{11}/'

    def scrape(self, username):
        self._connect('{}/{}/media'.format(self.base_url, username))

        if self._mode != 'silent':
            print('Crawling...')

        done = self.scrollToBottom()

        source = self.source()
        soup = bs(source, 'html.parser')

        # title = soup.find('title')
        # name = title.get_text().replace('Media Tweets by ', '').replace(' | Twitter', '')

        # avatar_url = soup.find("a", { "class" : "ProfileCardMini-avatar" }).get('data-resolved-url-large')
        # background_url = soup.find("div", { "class" : "ProfileCanopy-headerBg" }).find('img').get('src')

        tasks = []
        for div in soup.find_all('div', { "class" : "AdaptiveMedia-photoContainer" }):
            url = div.get('data-image-url')
            tasks.append((url+':large', username, get_filename(url)))

        if self._mode != 'silent':
            print('{} media are found.'.format(len(tasks)))

        return tasks

    def login(self, credentials_file):
        credentials = self.load_credentials(credentials_file)
        
        if credentials['email'] == '' or credentials['password'] == '':
            print('Either email or password is empty. Abort login.')
            return

        if self._mode != 'silent':
            print('Logging in as "{}"...'.format(credentials['email']))

        self._connect(self.login_url)
        time.sleep(self._login_pause_time)

        email = self._driver.find_element_by_tag_name('email')
        password = self._driver.find_element_by_tag_name('pass')
        buttons = self._driver.find_element_by_tag_name('login')

        username.send_keys(credentials['email'])
        password.send_keys(credentials['password'])
        button.click()
        time.sleep(self._login_pause_time)


class pixivScraper(Scraper):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name = 'pixiv'

        self.base_url = 'https://www.pixiv.net'
        self.post_url = 'https://www.pixiv.net/member_illust.php?id='
        self.login_url = 'https://accounts.pixiv.net/login'
        # self.post_regex = '/p/[ -~]{11}/'

    def scrape(self, id, content_type='all'):
        self._connect(self.post_url + id)
        self.id = id
        self.type = content_type

        if self._mode != 'silent':
            print('Crawling...')

        # TODO

        # get page num
        pager_container = self._driver.get_element_by_class_name('page-list')
        last_pager = pager_container.get_element_by_tag_name('li')[-1]
        num_page = int(last_pager.get_element_by_tag_name('a').text)
        print('# of page: {}'.format(num_page))

        # crawl each page
        for p in range(1, num_page+1):
            url = 'https://www.pixiv.net/member_illust.php?id={}&type={}&p={}'.format(self.id, self.type, p)
            self._driver._connect(url)
            time.sleep(self._next_page_pause_time)
            print(url)
        # scrape each post

        return

        done = self.scrollToBottom()

        source = self.source()
        soup = bs(source, 'html.parser')

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
        
        if credentials['username'] == '' or credentials['password'] == '':
            print('Either username or password is empty. Abort login.')
            return

        if self._mode != 'silent':
            print('Logging in as "{}"...'.format(credentials['username']))

        self._connect(self.login_url)
        time.sleep(self._login_pause_time)

        container = self._driver.find_element_by_id('container-login')

        username, password = container.find_elements_by_tag_name('input')
        buttons = container.find_element_by_tag_name('button')

        username.send_keys(credentials['username'])
        password.send_keys(credentials['password'])
        button.click()
        time.sleep(self._login_pause_time)
