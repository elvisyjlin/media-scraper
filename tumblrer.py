import argparse
import json
import os
import requests
import shutil
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from utils.helpers import log

API = {
    'base': 'https://www.tumblr.com', 
    'v1': {
        'read': '/api/read/json'
    }
}

VAR = {
    'save_path': '.', 
    'types': ['text', 'quote', 'photo', 'link', 'chat', 'video', 'audio']
}

def parse():
    parser = argparse.ArgumentParser(description="Tumblrer")
    parser.add_argument('urls', nargs='*', help='urls to crawl')
    parser.add_argument('--save_path', type=str, default='./download', help='path to save')
    parser.add_argument('--early_stop', action='store_true')
    return parser.parse_args()

def path(path):
    VAR['save_path'] = path

def get(url, start=0, num=50):
    url = url + API['v1']['read']
    params = {'start': start, 'num': num}
    log('Get {} with {}'.format(url, params))
    res = requests.get(url=url, params=params, verify=False)
    content = json.loads(res.text.replace('var tumblr_api_read = ', '')[:-2])
    del res
    return content

def download(img_url, filename):
    if os.path.exists(filename):
        return 1
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    log('Download {}'.format(img_url))
    res = requests.get(img_url, stream=True, timeout=10)
    with open(filename, 'wb') as f:
        shutil.copyfileobj(res.raw, f)
    del res
    return 0

def crawl(url, early_stop=False, start=0, num=50):
    print('Tumblrer Task', url)
    total = start + 1
    while start < total:
        content = get(url, start, num)
        if type(content) is not dict:
            start += 1
            continue
        with open('current.json', 'w') as f:
            f.write(json.dumps(content))
        blog_name = content['tumblelog']['name']
        start = content['posts-start']
        total = content['posts-total']
        posts = content['posts']
        print('[{}/{}]'.format(start, total), '# of posts: {}'.format(len(posts)))
        for post in posts:
            if 'photo-url-1280' in post:
                img_url = post['photo-url-1280']
                filename = os.path.join(VAR['save_path'], blog_name, post['type'], 
                                        str(post['id']) + '_' + img_url.rsplit('/', 1)[1])
                success = False
                while not success:
                    try:
                        res = download(img_url, filename)
                        success = True
                    except Exception as e:
                        print(e)
                        print('Sleep for 1 minutes...')
                        time.sleep(1 * 60)
                if early_stop and res == 1:
                    return 0
            else:
                print(post['id'], post['url'], post['type'])
            if 'photos' in post and post['photos'] != []:
                print('photos', len(post['photos']))
                for photo in post['photos']:
                    img_url = photo['photo-url-1280']
                    filename = os.path.join(VAR['save_path'], blog_name, post['type'], 
                                            str(post['id']) + '_' + img_url.rsplit('/', 1)[1])
                    success = False
                    while not success:
                        try:
                            download(img_url, filename)
                            success = True
                        except Exception as e:
                            print(e)
                            print('Sleep for 1 minutes...')
                            time.sleep(1 * 60)
        start += num
    return 0

if __name__ == '__main__':
    args = parse()
    print(args)
    path(args.save_path)
    for url in args.urls:
        crawl(url, args.early_stop)