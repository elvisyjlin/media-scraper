#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import mediascrapers
import os
import sys

if __name__ == '__main__':
    scraper = mediascrapers.TwitterScraper(scroll_pause = 1.0, mode='normal', debug=False)
    if os.path.exists('credentials.json'):
        scraper.login('credentials.json')
    for username in sys.argv[1:]:
        if username[0] == '@':
            username = username[1:]
        tasks = scraper.scrape(username)
        scraper.download(tasks=tasks, path='download/twitter')