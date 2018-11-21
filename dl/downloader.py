import argparse
import json
import os
import requests
import shutil
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Downloader():
    def __init__(self):
        self.description = 'Downloader'
        self.keyword = 'url'
        self.save_path = '.'

    def parse(self):
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('keywords', nargs='*', help=self.keyword+'s to crawl (or files containing '+self.keyword+'s)')
        parser.add_argument('-s', '--save_path', type=str, help='path to save')
        parser.add_argument('-e', '--early_stop', action='store_true')
        return parser.parse_args()
    
    def get(self, url):
        pass

    def download(self, img_url, filename):
        if os.path.exists(filename):
            print('File exists ({}). Skip {}'.format(filename, img_url))
            return False
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        print('Downloading {} as {}'.format(img_url, filename))
        res = requests.get(img_url, stream=True, timeout=10, verify=False)
        with open(filename, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        del res
        return True
    
    def run(self):
        args = self.parse()
        print(args)

        if args.save_path is not None:
            self.save_path = args.save_path

        for keyword in args.keywords:
            if keyword.endswith('.txt') and os.path.exists(keyword):
                with open(keyword, 'r') as f:
                    kws = [kw.strip() for kw in f.read().split() if not kw.startswith('#')]
                    print('In file', keyword, 'finds {}s:'.format(self.keyword), kws)
                    for kw in kws:
                        self.crawl(kw, args.early_stop)
            else:
                self.crawl(keyword, args.early_stop)

if __name__ == '__main__':
    pass