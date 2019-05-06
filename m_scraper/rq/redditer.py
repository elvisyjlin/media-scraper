#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import requests
import os
import time
import json
from .downloader import Downloader
from .utils.helpers import get_imgur, get_gfycat, requests_get

class Redditer(Downloader):
    def __init__(self):
        super(Redditer, self).__init__()
        self.description = 'Redditer'
        self.identifier = 'reddit'
        self.keyword = 'subreddit'
        self.save_path = './download_reddit'
        self.api = {
            'base': 'https://www.reddit.com', 
            'posts': 'https://www.reddit.com/r/{}.json?after={}', 
            'search': 'https://www.reddit.com/subreddits/search.json?q={}&include_over_18=on'
        }

    def safe_download(self, subreddit, name, img_url):
        filename = os.path.join(self.save_path, subreddit, name + '.' + os.path.basename(img_url).split('?')[0])
        success = False
        while not success:
            try:
                self.download(img_url, filename)
                success = True
            except requests.exceptions.ConnectionError as e:
                print(e)
                print(img_url, filename)
                print('Skip this.')
                break
            except Exception as e:
                print(e)
                print(img_url, filename)
                print('Sleep for 1 hour...')
                time.sleep(1*60*60)

    def crawl(self, subreddit, early_stop=False):
        print('Redditer Task:', subreddit)

        userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
        headers = {
            'User-Agent': userAgent
        }

        after = ''
        done = False

        while not done:
            text = requests_get(self.api['posts'].format(subreddit, after), headers=headers)
            red = json.loads(text)
            print(len(red['data']['children']))

            for child in red['data']['children']:
                name = child['data']['name']
                img_url = child['data']['url']
                if os.path.splitext(img_url)[1] == '':
                    if 'imgur.com/' in img_url:
                        img_url = get_imgur(img_url)
                        if img_url is not None:
                            self.safe_download(subreddit, name, img_url)
                    elif 'gfycat.com/' in img_url:
                        for vid_url in get_gfycat(img_url):
                            self.safe_download(subreddit, name, vid_url)
                    else:
                        print('No media in [{}]. Skip it.'.format(img_url))
                        continue
                else:
                    self.safe_download(subreddit, name, img_url)
                after = name

            if len(red['data']['children']) == 0:
                done = True

if __name__ == '__main__':
    redditer = Redditer()
    redditer.run()