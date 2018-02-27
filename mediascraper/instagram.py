#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import mediascrapers
import sys

if __name__ == '__main__':
    scraper = mediascrapers.InstagramScraper(scroll_pause = 1.0, mode='normal', debug=False)
    scraper.username(sys.argv[1])
    scraper.scrape(path='download/instagram')