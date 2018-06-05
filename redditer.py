import argparse
import requests
import os
import shutil
import time
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from utils.helpers import log, get_imgur, get_gfycat

API = {
    'base': 'https://www.reddit.com', 
    'posts': 'https://www.reddit.com/r/{}.json?after={}', 
    'search': 'https://www.reddit.com/subreddits/search.json?q={}&include_over_18=on'
}

VAR = {
    'save_path': '.'
}

def parse():
    parser = argparse.ArgumentParser(description="Redditer")
    parser.add_argument('subreddits', nargs='*', help='subreddits to crawl')
    parser.add_argument('-s', '--save_path', default='./download_reddit', help='path to save')
    parser.add_argument('-e', '--early_stop', action='store_true')
    return parser.parse_args()

def path(path):
    VAR['save_path'] = path

def download(img_url, filename):
    if os.path.exists(filename):
        log('{} already exists and ignore {}'.format(filename, img_url), 'log_reddit.txt')
        return 1
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    log('Download {} as {}'.format(img_url, filename), 'log_reddit.txt')
    res = requests.get(img_url, stream=True, timeout=10, verify=False)
    with open(filename, 'wb') as f:
        shutil.copyfileobj(res.raw, f)
    del res
    return 0

def safe_download(subreddit, name, img_url):
    filename = os.path.join(VAR['save_path'], subreddit, name + '.' + os.path.basename(img_url).split('?')[0])
    success = False
    while not success:
        try:
            download(img_url, filename)
            success = True
        except Exception as e:
            print(e)
            print(img_url, filename)
            with open('error_reddit', 'w', encoding='utf-8') as f:
                f.write(res)
            print('Sleep for 1 hour...')
            time.sleep(1*60*60)
    
def crawl(subreddit, early_stop=False):
    print('Redditer Task:', subreddit)
    
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
    headers = {
        'User-Agent': userAgent
    }
    
    after = ''
    done = False
    
    while not done:
        res = requests.get(API['posts'].format(subreddit, after), headers=headers)
        red = json.loads(res.text)
        print(len(red['data']['children']))
            
        for child in red['data']['children']:
            name = child['data']['name']
            img_url = child['data']['url']
            if os.path.splitext(img_url)[1] == '':
                if 'imgur' in img_url:
                    img_url = get_imgur(img_url)
                    safe_download(subreddit, name, img_url)
                elif 'gfycat' in img_url:
                    for vid_url in get_gfycat(img_url):
                        safe_download(subreddit, name, vid_url)
                else:
                    log('No media in [{}]. Skip it.'.format(img_url))
                    continue
            else:
                safe_download(subreddit, name, img_url)
            after = name

        if len(red['data']['children']) == 0:
            done = True

if __name__ == '__main__':
    args = parse()
    print(args)
    path(args.save_path)
    for subreddit in args.subreddits:
        if subreddit.endswith('.txt') and os.path.exists(subreddit):
            with open(subreddit, 'r') as f:
                uns = [un.strip() for un in f.read().split()]
                print('In file', subreddit, 'finds usernames:', uns)
                for un in uns:
                    crawl(un, args.early_stop)
        else:
            crawl(subreddit, args.early_stop)