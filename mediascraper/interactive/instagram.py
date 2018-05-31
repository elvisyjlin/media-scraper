#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import mediascrapers
import os
import sys

def input_username():
    return input('Enter a username (ENTER to exit): ').strip()

if __name__ == '__main__':
    print('Starting InstagramScraper...')
    scraper = mediascrapers.InstagramScraper(scroll_pause = 1.0, mode='normal', debug=False)
    if os.path.exists('credentials.json'):
        scraper.login('credentials.json')
    username = input_username()
    while username != '':
        tasks = scraper.scrape(username)
        scraper.download(tasks=tasks, path='download/instagram')
        username = input_username()