#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import time
import os
from .downloader import Downloader
from .utils.instagram import *

class Instagramer(Downloader):
    def __init__(self):
        super(Instagramer, self).__init__()
        self.description = 'Instagramer'
        self.identifier = 'instagram'
        self.keyword = 'username'
        self.save_path = './download_instagram'
        self.api = {
            'base': 'https://www.instagram.com', 
            'posts': 'https://www.instagram.com/graphql/query/?query_hash={}&variables={{"id":"{}","first":{},"after":"{}"}}', 
            'query_hash': '9ca88e465c3f866a76f7adee3871bdd8', 
            'first': 12
        }

    def perform(self, tasks, username, early_stop=False):
        print('# of tasks:', len(tasks))
        success = True
        for img_url, filename in tasks:
            success = False
            while not success:
                try:
                    res = self.download(img_url, os.path.join(self.save_path, username, filename))
                    success = True
                except Exception as e:
                    print(e)
                    print('Sleep for 1 hour...')
                    time.sleep(1 * 60 * 60)
            success = success and res
            if early_stop and not success:
                return res
        return res
    
    def crawl(self, username, early_stop=False):
        print('Instagramer Task:', username)
        tasks, end_cursor, has_next, length, user_id, rhx_gis, csrf_token = get_first_page(username)
        if tasks is None:
            return -1
        res = self.perform(tasks, username, early_stop=early_stop)
        if early_stop and res == 1:
            return 0
        while has_next:
            tasks, end_cursor, has_next, length = get_following_page(query_hash, user_id, end_cursor, rhx_gis, csrf_token)
            res = self.perform(tasks, username, early_stop=early_stop)
            if early_stop and res == 1:
                return 0

if __name__ == '__main__':
    instagramer = Instagramer()
    instagramer.run()