#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from .downloader import Downloader
from .utils.helpers import save_json

class Pixiver(Downloader):
    def __init__(self):
        super(Pixiver, self).__init__()
        self.description = 'Pixiver'
        self.identifier = 'pixiv'
        self.keyword = 'userid'
        self.save_path = './download_pixiv'
        # Daily Ranking 'https://www.pixiv.net/ranking.php?mode=daily&p=1&format=json'
    
    def login(self, username, password):
        print('Logging in pixiv account...')
        res = self.sess.get('https://accounts.pixiv.net/login')
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            post_key = soup.select('input[name==post_key]')[0]['value']
        else:
            print(res.text)
            raise Exception(res.status_code)
        
        form_data = {
            'captcha': None,
            'g_recaptcha_response': None,
            'pixiv_id': username,
            'password': password,
            'post_key': post_key,
            'source': 'accounts',
            'ref': None,
            'return_to': 'https://www.pixiv.net/'
        }
        res = self.sess.post('https://accounts.pixiv.net/api/login', data=form_data)
        if res.status_code == 200:
            print(res.text)
        else:
            print(res.text)
            raise Exception(res.status_code)
        print('Logged in successfully.')
    
    def download_illust(self, id, path):
        data_file = os.path.join(path, '{:s}.json'.format(id))
        headers = {
            'Referer': 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id={:s}'.format(id)
        }
        if os.path.exists(data_file):
            return True
        res = self.sess.get('https://www.pixiv.net/ajax/illust/{:s}'.format(id))
        if res.status_code == 200:
            data = res.json()
            first_image_url = data['body']['urls']['original']
            first_image_filename = os.path.join(path, os.path.basename(first_image_url).split('?', 1)[0])
            page_count = data['body']['pageCount']
            illust_type = data['body']['illustType']  # 0: single, 1: multiple, 2: animated
            if illust_type == 0:
                self.download(first_image_url, first_image_filename, headers=headers)
            elif illust_type == 1:
                res = self.sess.get('https://www.pixiv.net/ajax/illust/{:s}/pages'.format(id))
                if res.status_code == 200:
                    data = res.json()
                    for page in data['body']:
                        url = page['urls']['original']
                        filename = os.path.join(path, os.path.basename(url).split('?', 1)[0])
                        self.download(url, filename, headers=headers)
                else:
                    print(res.text)
                    raise Exception(res.status_code)
            elif illust_type == 2:
                self.download(first_image_url, first_image_filename, headers=headers)
                res = self.sess.get('https://www.pixiv.net/ajax/illust/{:s}/ugoira_meta'.format(id))
                if res.status_code == 200:
                    data = res.json()
                    zip_url = data['body']['src']
                    zip_filename = os.path.join(path, os.path.basename(zip_url).split('?', 1)[0])
                    self.download(zip_url, zip_filename, headers=headers)
                    zip_url = data['body']['originalSrc']
                    zip_filename = os.path.join(path, os.path.basename(zip_url).split('?', 1)[0])
                    self.download(zip_url, zip_filename, headers=headers)
                else:
                    print(res.text)
                    raise Exception(res.status_code)
            else:
                raise Exception('Invalid illustType: {}'.format(illust_type))
            save_json(data, data_file)  # Save JSON data once images are downloaded successfully
        else:
            print(res.text)
            raise Exception(res.status_code)
        return False
    
    def crawl(self, userid, early_stop=False):
        print('Pixiver Task:', userid)
        url = 'https://www.pixiv.net/ajax/user/{:s}/profile/all'.format(userid)
        res = self.sess.get(url)
        if res.status_code == 200:
            # 'manga', 'bookmarkCount', 'mangaSeries', 'illusts', 'novels', 'pickup', 'novelSeries'
            data = res.json()
            data_file = os.path.join(self.save_path, userid, 'all.json')
            if os.path.exists(data_file):
                i = 2
                while os.path.exists(data_file):
                    data_file = os.path.join(self.save_path, userid, 'all-{:d}.json'.format(i))
                    i += 1
            save_json(data, data_file)
            for illust_id in tqdm(reversed(sorted(data['body']['illusts'].keys()))):
                # From the latest illust to the oldest one
                path = os.path.join(self.save_path, userid, 'illusts')
                done = self.download_illust(illust_id, path)
                if early_stop and done:
                    break
            for manga_id in tqdm(reversed(sorted(data['body']['manga'].keys()))):
                # From the latest manga to the oldest one
                path = os.path.join(self.save_path, userid, 'manga')
                done = self.download_illust(manga_id, path)
                if early_stop and done:
                    break
        else:
            print(res.text)
            raise Exception(res.status_code)

if __name__ == '__main__':
    pixiver = Pixiver()
    pixiver.run()