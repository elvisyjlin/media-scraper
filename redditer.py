import requests
import os
import time
import json
from downloader import Downloader
from utils.helpers import log, get_imgur, get_gfycat

class Redditer(Downloader):
    def __init__(self):
        super(Tumblrer).__init__()
        self.description = 'Redditer'
        self.keyword = 'subreddit'
        self.save_path = './download_reddit'
        self.log_path = 'log_reddit.txt'
        self.api = {
            'base': 'https://www.reddit.com', 
            'posts': 'https://www.reddit.com/r/{}.json?after={}', 
            'search': 'https://www.reddit.com/subreddits/search.json?q={}&include_over_18=on'
        }

    def download(self, img_url, filename):
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

    def safe_download(self, subreddit, name, img_url):
        filename = os.path.join(self.save_path, subreddit, name + '.' + os.path.basename(img_url).split('?')[0])
        success = False
        while not success:
            try:
                self.download(img_url, filename)
                success = True
            except requests.exceptions.ConnectionError as e:
                print(e)
                print(img_url, filename)
                print('Skip this.')
                break
            except Exception as e:
                print(e)
                print(img_url, filename)
                print('Sleep for 1 hour...')
                time.sleep(1*60*60)

    def crawl(self, subreddit, early_stop=False):
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
                    if 'imgur.com/' in img_url:
                        img_url = get_imgur(img_url)
                        if img_url is not None:
                            self.safe_download(subreddit, name, img_url)
                    elif 'gfycat.com/' in img_url:
                        for vid_url in get_gfycat(img_url):
                            self.safe_download(subreddit, name, vid_url)
                    else:
                        log('No media in [{}]. Skip it.'.format(img_url))
                        continue
                else:
                    self.safe_download(subreddit, name, img_url)
                after = name

            if len(red['data']['children']) == 0:
                done = True

if __name__ == '__main__':
    redditer = Redditer()
    redditer.run()