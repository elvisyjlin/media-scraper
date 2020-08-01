#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import os
# class file:
#     def __init__(self):
#         continue
def get_basename(filename):
    return filename.rsplit('.', 1)[0]

def get_extension(filename):
    return filename.rsplit('.', 1)[1]

def rename_file(filename, name):
    print(filename, name)
    return '{}.{}'.format(name, get_extension(filename))

def safe_makedirs(path):
    # print(f'PATH: {path}')
    if not os.path.exists(path):
        os.makedirs(path)
