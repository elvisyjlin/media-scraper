#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

def largest_image_url(resources):
    return max(resources, key=lambda x: x['config_height']*x['config_width'])['src']

def node_name(node):
    return '{},{}'.format(node['id'], node['shortcode'])

def parse_node(node, name=''):
    tasks = []

    if name == '':
        name = node_name(node)
    else:
        name += ' ' + node_name(node)

    display_resources = node['display_resources']
    # find the highest resolution image
    url = largest_image_url(display_resources)
    # download(url, path=save_path, rename=name, replace=False)
    tasks.append((url, name))

    typename = node['__typename']
    if typename == 'GraphImage':
        pass
    elif typename == 'GraphSidecar':
        edges = node['edge_sidecar_to_children']['edges']
        for edge in edges:
            # parse_node(edge['node'], name, save_path)
            tasks += parse_node(edge['node'], name)
    elif typename == 'GraphVideo':
        url = node['video_url']
        # download(url, path=save_path, rename=name, replace=False)
        tasks.append((url, name))
    else:
        print('Error: unsupported typename "{}".'.format(typename))

    return tasks