#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import json
import requests
import os
import time

def log(msg, file='log.txt'):
    print(msg)
    with open(file, 'a') as f:
        f.write(msg + '\n')

def requests_get(url, fn=None, **kwarg):
    res = None
    data = None
    success = False
    while not success:
        try:
            res = requests.get(url, **kwarg)
            text = res.text
            data = text if fn is None else fn(text)
            success = True
        except Exception as e:
            print('Error when getting', url)
            f = open('error.txt', 'w', encoding='utf-8')
            f.write(url + '\n\n')
            if res is not None:
                f.write(text + '\n\n')
            f.write(str(e))
            f.close()
            print('Error details are saved in error.txt')
            print('Sleep for 1 hour...')
            time.sleep(1 * 60 * 60)
    return data

def get_imgur(url):
    '''
    Returns an image url (jpg, png, gif, ...) of the given Imgur url.
    '''
    
    assert 'imgur.com/' in url, 'Error occurs when parsing url [{}]'.format(url)
    
    IMGUR_URL = 'https://i.imgur.com/{}.{}'
    IMGUR_JPG = 'https://i.imgur.com/{}.jpg'
    
    img_id = url.rsplit('/', 1)[1]
    res = requests.head(IMGUR_JPG.format(img_id))
    
    if int(res.headers['Content-Length']) == 0:
        return None
    
    try:
        content_type = res.headers['Content-Type']
    except Exception as e:
        print(IMGUR_JPG.format(img_id))
        print(res.headers)
        raise e
        
    ext = content_type.split('/')[1]
    ext = 'jpg' if ext == 'jpeg' else ext
    
    return IMGUR_URL.format(img_id, ext)
    

def get_gfycat(url):
    '''
    Returns an mp4 url and a webm url of the given Gfycat url.
    '''
    
    assert 'gfycat.com/' in url, 'Error occurs when parsing url [{}]'.format(url)
    
    GFYCAT_MP4  = 'https://giant.gfycat.com/{}.mp4'
    GFYCAT_WEBM = 'https://giant.gfycat.com/{}.webm'
    
    name = url.rsplit('/', 1)[1]
    
    return [GFYCAT_MP4.format(name), 
            GFYCAT_WEBM.format(name)]

def save_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    json.dump(data, open(filename, 'w', encoding='utf-8'))

def url_basename(url):
    filename = os.path.basename(url)
    if '?' in filename:
        filename = filename.split('?', 1)[0]
    return filename