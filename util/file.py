#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import os

def get_basename(filename):
    return filename.rsplit('.', 1)[0]

def get_extension(filename):
    return filename.rsplit('.', 1)[1]

def rename_file(filename, name):
    return '{}.{}'.format(name, get_extension(filename))

def safe_makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)