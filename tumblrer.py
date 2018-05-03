import argparse
import requests
import json
import os
import shutil
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
    parser.add_argument('url', help='url to crawl')
    parser.add_argument('--save_path', default='./download', help='path to save')
    return parser.parse_args()

def path(path):
    VAR['save_path'] = path

def get(url, start=0, num=50):
    url = url + API['v1']['read']
    params = {'start': start, 'num': num}
    res = requests.get(url=url, params=params, verify=False)
    content = json.loads(res.text.replace('var tumblr_api_read = ', '')[:-2])
    del res
    return content

def download(img_url, filename):
    file = os.path.join(VAR['save_path'], filename)
    if os.path.exists(file):
        return
    res = requests.get(img_url, stream=True)
    with open(file, 'wb') as f:
        shutil.copyfileobj(res.raw, f)
    del res

def crawl(url, start=0, num=50):
    print('Tumblrer Task', url)
    total = start + 1
    while start < total:
        content = get(url, start, num)
        start = content['posts-start']
        total = content['posts-total']
        posts = content['posts']
        print('[{}/{}]'.format(start, total), '# of posts: {}'.format(len(posts)))
        for post in posts:
            img_url = post['photo-url-1280']
            filename = post['type'] + '/' + post['id'] + '_' + img_url.rsplit('/', 1)[1]
            download(img_url, filename)
        start += num

if __name__ == '__main__':
    args = parse()
    path(args.save_path)
    for t in VAR['types']:
        os.makedirs(os.path.join(VAR['save_path'], t), exist_ok=True)
    crawl(args.url)