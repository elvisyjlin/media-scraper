import argparse
import requests
import urllib
import os
import shutil
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from utils.instagram import *
from utils.helpers import log

API = {
    'base': 'https://www.instagram.com', 
    'posts': 'https://www.instagram.com/graphql/query/?query_hash={}&variables={{"id":"{}","first":{},"after":"{}"}}', 
    'query_hash': '9ca88e465c3f866a76f7adee3871bdd8', 
    'first': 12
}

VAR = {
    'save_path': '.'
}

def parse():
    parser = argparse.ArgumentParser(description="Instagramer")
    parser.add_argument('usernames', nargs='*', help='usernames to crawl')
    parser.add_argument('--save_path', default='./download_instagram', help='path to save')
    parser.add_argument('--early_stop', action='store_true')
    return parser.parse_args()

def path(path):
    VAR['save_path'] = path

def download(img_url, filename):
    if os.path.exists(filename):
        log('{} already exists and ignore {}'.format(filename, img_url), 'log_instagram.txt')
        return 1
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    log('Download {} as {}'.format(img_url, filename), 'log_instagram.txt')
    res = requests.get(img_url, stream=True, timeout=10, verify=False)
    with open(filename, 'wb') as f:
        shutil.copyfileobj(res.raw, f)
    del res
    return 0

def perform(tasks, username):
    print('# of tasks:', len(tasks))
    res = 0
    for img_url, filename in tasks:
        success = False
        while not success:
            try:
                res_t = download(img_url, os.path.join(VAR['save_path'], username, filename))
                success = True
            except Exception as e:
                print(e)
                print('Sleep for 1 hour...')
                time.sleep(1 * 60 * 60)
        res = res or res_t
    return res
    
def crawl(username, early_stop=False):
    print('Instagramer Task', username)
    tasks, end_cursor, has_next, length, user_id, rhx_gis, csrf_token = getFirstPage(username)
    res = perform(tasks, username)
    if early_stop and res == 1:
        return 0
    while has_next:
        tasks, end_cursor, has_next, length = getFollowingPage(query_hash, user_id, end_cursor, rhx_gis, csrf_token)
        res = perform(tasks, username)
        if early_stop and res == 1:
            return 0

if __name__ == '__main__':
    args = parse()
    print(args)
    path(args.save_path)
    for username in args.usernames:
        crawl(username, args.early_stop)