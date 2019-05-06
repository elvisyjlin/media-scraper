#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 m-scraper.py [rq/bs] [instagram/twitter/tumblr/reddit] [options]')
        sys.exit(1)
    
    module = sys.argv[1]
    site = sys.argv[2]
    
    if module == 'rq' and site == 'instagram':
        import m_scraper.rq
        scraper = m_scraper.rq.Instagramer()
    elif module == 'rq' and site == 'tumblr':
        import m_scraper.rq
        scraper = m_scraper.rq.Tumblrer()
    elif module == 'rq' and site == 'reddit':
        import m_scraper.rq
        scraper = m_scraper.rq.Redditer()
    elif module == 'rq' and site == 'pixiv':
        import m_scraper.rq
        scraper = m_scraper.rq.Pixiver()
    elif module == 'rq' and site == 'tiktok':
        import m_scraper.rq
        scraper = m_scraper.rq.TikToker()
    else:
        print('`m-scraper` does not support', module, site)
        sys.exit(1)
        
    scraper.run(sys.argv[3:])