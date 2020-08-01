#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import os
import urllib
import requests
from cutil.file import rename_file, safe_makedirs
from cutil.twitter import twitter_m3u8

def get_filename(url):
    # print(url)
    return url.rsplit('/')[-1].split(':')[0]

def complete_url(url, current_url):
    if ':' not in url:
        if url.startswith('//'):
            url = 'http:' + url
        elif url.startswith('/'):
            if url.endswith('/'):
                base_url = '/'.join(current_url.split('/')[:3])
                url = base_url + url
            else:
                dir_url = current_url.rsplit('/', 1)[0]
                url = dir_url + url
        else:
            dir_url = current_url.rsplit('/', 1)[0]
            url = dir_url + '/' + url
    return url

def download(url, path='.', rename=None, replace=True,num=1):

    n=num
    if('.jpg' in url or 'format=jpg' in url ):
        filename=str(n)+'.jpg'
    elif('.jpeg' in url or 'format=jpeg' in url ):
        filename=str(n)+'.jpeg'
    elif('.svg' in url or 'format=svg' in url ):
        return 
    elif('.png' in url or 'format=png' in url ):
        filename=str(n)+'.png'
    else:
        filename=str(n)+'.jpeg'
    file = os.path.join(path, filename)


    if '.m3u8' in url:
        twitter_m3u8(url, file.replace('.m3u8', '.ts'))
    else:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            safe_makedirs(path)
            with open(file, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            print('Error: status code of {} "{}" is {}.'.format(filename, url, r.status_code))

# Guess the type of url by its mime format.
#
# IANA - MIME
# Media Types: http://www.iana.org/assignments/media-types/media-types.xhtml

import mimetypes

def get_mimetype(url):
    return mimetypes.guess_type(url, strict=False)[0]

def is_image(url):
    mimetype = get_mimetype(url)
    return None if mimetype is None else mimetype.split('/')[0] == 'image'

def is_video(url):
    mimetype = get_mimetype(url)
    return None if mimetype is None else mimetype.split('/')[0] == 'video'

def is_media(url,strict=True):
    mimetype = get_mimetype(url)
    if(strict==False):
        if('format=jpg' in url or 'format=jpeg' in url or 'format=svg' in url or 'format=png' in url or'format=png' in url):
            return True
    return False if mimetype is None else mimetype.split('/')[0] == 'image' or mimetype.split('/')[0] == 'video'
    return True