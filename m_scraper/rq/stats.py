#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import os

if __name__ == '__main__':
    num_images = 0
    subfolders = os.listdir('./download') if os.path.exists('./download') else []
    for subfolder in subfolders:
        num = len(os.listdir(os.path.join('./download', subfolder, 'photo')))
        num_images += num
        print(subfolder, num)
        
    print('=== Tumblrer Stats ===')
    print('# of galleries:', len(subfolders))
    print('# of photos:', num_images)
    print('======================')
    
    num_images = 0
    subfolders = os.listdir('./download_instagram') if os.path.exists('./download_instagram') else []
    for subfolder in subfolders:
        num = len(os.listdir(os.path.join('./download_instagram', subfolder)))
        num_images += num
        print(subfolder, num)
        
    print('=== Instagramer Stats ===')
    print('# of galleries:', len(subfolders))
    print('# of media:', num_images)
    print('======================')