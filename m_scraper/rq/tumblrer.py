#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import json
import time
import os
from .downloader import Downloader
from .utils.helpers import requests_get

# VAR = {
#     'save_path': '.', 
#     'types': ['text', 'quote', 'photo', 'link', 'chat', 'video', 'audio']
# }
    
class Tumblrer(Downloader):
    def __init__(self, target='media'):
        super(Tumblrer, self).__init__()
        self.description = 'Tumblrer'
        self.identifier = 'tumblr'
        self.keyword = 'sitename'
        self.save_path = './download_tumblr'
        self.api = {
            'base': 'https://www.tumblr.com', 
            'v1': {
                'read': '/api/read/json'
            }
        }
        
        if target == 'media':
            self.crawl = self.crawl_media
        elif target == 'article':
            self.crawl = self.crawl_article

    def get(self, sitename, start=0, num=50):
        url = 'https://' + sitename + self.api['v1']['read']
        params = {'start': start, 'num': num}
        print('Get {} with {}'.format(url, params))
        text = requests_get(url=url, params=params, verify=False)
        content = json.loads(text.replace('var tumblr_api_read = ', '')[:-2])
        return content
    
    def crawl_media(self, sitename, early_stop=False, start=0, num=50):
        print('Tumblrer Task:', sitename)
        total = start + 1
        while start < total:
            content = self.get(sitename, start, num)
            if type(content) is not dict:
                start += 1
                continue
            with open('current.json', 'w') as f:
                f.write(json.dumps(content))
            blog_name = content['tumblelog']['name']
            start = content['posts-start']
            total = content['posts-total']
            posts = content['posts']
            print('[{}/{}]'.format(start, total), '# of posts: {}'.format(len(posts)))
            for post in posts:
                if 'photo-url-1280' in post:
                    img_url = post['photo-url-1280']
                    filename = os.path.join(self.save_path, blog_name, post['type'], 
                                            str(post['id']) + '.' + img_url.rsplit('/', 1)[1])
                    success = False
                    while not success:
                        try:
                            res = self.download(img_url, filename)
                            success = True
                        except Exception as e:
                            print(e)
                            print('Sleep for 1 minute...')
                            time.sleep(1 * 60)
                    if early_stop and res == 1:
                        return 0
                else:
                    print(post['id'], post['url'], post['type'])
                if 'photos' in post and post['photos'] != []:
                    print('photos', len(post['photos']))
                    for photo in post['photos']:
                        img_url = photo['photo-url-1280']
                        filename = os.path.join(self.save_path, blog_name, post['type'], 
                                                str(post['id']) + '.' + img_url.rsplit('/', 1)[1])
                        success = False
                        while not success:
                            try:
                                self.download(img_url, filename)
                                success = True
                            except Exception as e:
                                print(e)
                                print('Sleep for 1 minute...')
                                time.sleep(1 * 60)
            start += num
        return 0
    
    def crawl_article(self, sitename, early_stop=False, start=0, num=50):
        print('Tumblrer Task:', sitename)
        total = start + 1
        total_posts = []
        while start < total:
            content = self.get(sitename, start, num)
            if type(content) is not dict:
                start += 1
                continue
            with open('current.json', 'w') as f:
                f.write(json.dumps(content))
            blog_name = content['tumblelog']['name']
            start = content['posts-start']
            total = content['posts-total']
            posts = content['posts']
            total_posts += posts
            print('[{}/{}]'.format(start, total), '# of posts: {}'.format(len(posts)))
            start += num
        with open('posts.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(total_posts))
        return 0

if __name__ == '__main__':
    tumblrer = Tumblrer(target="article")
    tumblrer.run()