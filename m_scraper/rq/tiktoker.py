#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import os
from .downloader import Downloader
from .utils.helpers import save_json

class TikToker(Downloader):
    def __init__(self):
        super(TikToker, self).__init__()
        self.description = 'TikToker'
        self.identifier = 'tiktok'
        self.keyword = 'userid'
        self.save_path = './download_tiktok'
    
    def crawl(self, user_id, early_stop=False):
        path = os.path.join(self.save_path, user_id)
        max_cursor = '0'
        min_cursor = '0'
        extra_params = ''
        page_url = 'https://www.tiktok.com/share/user/{:s}'.format(user_id)
        headers = {
            'Referer': page_url,
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'
        }
        data = None
        done = False
        while not done:
            data_url = 'https://www.tiktok.com/share/item/list?id={:s}&type=1&count=100&maxCursor={:s}&minCursor={:s}{:s}'.format(user_id, max_cursor, min_cursor, extra_params)
            res = self.sess.get(data_url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                if 'body' not in data:
                    print(data)
                    raise Exception('body not found')
                itemListData = data['body']['itemListData']
                max_cursor = data['body']['maxCursor']
                done = not data['body']['hasMore']
                for item in data['body']['itemListData']:
                    video_id = item['itemInfos']['id']
                    cover_urls = item['itemInfos']['covers']
                    cover_origin_urls = item['itemInfos']['coversOrigin']
                    video_urls = item['itemInfos']['video']['urls']
                    assert len(cover_urls) == 1, 'Got {:d} cover urls.'.format(len(cover_urls))
                    assert len(cover_origin_urls) == 1, 'Got {:d} cover urls.'.format(len(cover_origin_urls))
                    assert len(video_urls) == 4, 'Got {:d} video urls.'.format(len(video_urls))
                    
                    data_path = os.path.join(path, video_id + '.json')
                    if early_stop and os.path.exists(data_path):
                        done = True
                        break
                    
                    video_url = video_urls[2]
                    video_filname = os.path.join(path, video_id + '_watermark.mp4')
                    self.download(video_url, video_filname, headers)
                    video_no_watermark_url = video_urls[2].replace('watermark=1', 'watermark=0')
                    video_no_watermar_filename = os.path.join(path, video_id + '.mp4')
                    self.download(video_no_watermark_url, video_no_watermar_filename, headers)
                    cover_url = cover_urls[0]
                    cover_filename = os.path.join(path, video_id + '_cover.jpg')
                    self.download(cover_url, cover_filename, headers)
                    cover_origin_url = cover_origin_urls[0]
                    cover_origin_filename = os.path.join(path, video_id + '_cover_origin.jpg')
                    self.download(cover_origin_url, cover_origin_filename, headers)
                    save_json(item, data_path)
            else:
                print(res.text)
                raise Exception(res.status_code)
        if data is not None:
            user_data = dict(data)
            del data['body']['itemListData']
            del data['body']['hasMore']
            del data['body']['maxCursor']
            del data['body']['minCursor']
            save_json(user_data, os.path.join(self.save_path, user_id + '.json'))

if __name__ == '__main__':
    tiktoker = TikToker()
    tiktoker.run()