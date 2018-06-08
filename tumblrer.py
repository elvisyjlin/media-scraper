import requests
import json
import time
import os
from downloader import Downloader

# VAR = {
#     'save_path': '.', 
#     'types': ['text', 'quote', 'photo', 'link', 'chat', 'video', 'audio']
# }
    
class Tumblrer(Downloader):
    def __init__(self):
        super(Tumblrer).__init__()
        self.description = 'Tumblrer'
        self.keyword = 'sitename'
        self.save_path = './download_tumblr'
        self.log_path = 'log_tumblr.txt'
        self.api = {
            'base': 'https://www.tumblr.com', 
            'v1': {
                'read': '/api/read/json'
            }
        }

    def get(self, sitename, start=0, num=50):
        url = sitename + self.api['v1']['read']
        params = {'start': start, 'num': num}
        log('Get {} with {}'.format(url, params))
        res = requests.get(url=url, params=params, verify=False)
        content = json.loads(res.text.replace('var tumblr_api_read = ', '')[:-2])
        del res
        return content
    
    def crawl(self, sitename, early_stop=False, start=0, num=50):
        print('Tumblrer Task:', sitename)
        total = start + 1
        while start < total:
            content = self.get(sitename, start, num)
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
                    filename = os.path.join(self.save_path, blog_name, post['type'], 
                                            str(post['id']) + '.' + img_url.rsplit('/', 1)[1])
                    success = False
                    while not success:
                        try:
                            res = self.download(img_url, filename)
                            success = True
                        except Exception as e:
                            print(e)
                            print('Sleep for 1 minute...')
                            time.sleep(1 * 60)
                    if early_stop and res == 1:
                        return 0
                else:
                    print(post['id'], post['url'], post['type'])
                if 'photos' in post and post['photos'] != []:
                    print('photos', len(post['photos']))
                    for photo in post['photos']:
                        img_url = photo['photo-url-1280']
                        filename = os.path.join(self.save_path, blog_name, post['type'], 
                                                str(post['id']) + '.' + img_url.rsplit('/', 1)[1])
                        success = False
                        while not success:
                            try:
                                self.download(img_url, filename)
                                success = True
                            except Exception as e:
                                print(e)
                                print('Sleep for 1 minute...')
                                time.sleep(1 * 60)
            start += num
        return 0

if __name__ == '__main__':
    tumblrer = Tumblrer()
    tumblrer.run()