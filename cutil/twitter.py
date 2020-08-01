import requests as r
import json as j
import re

def get_twitter_video_url(id):
    headers = {
        'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw'
    }

    url = 'https://api.twitter.com/1.1/videos/tweet/config/{}.json'.format(id)
    res = r.get(url, headers=headers)
    post = j.loads(res.text)
    return post['posterImage'], post['track']['playbackUrl'].rsplit('?', 1)[0]

def twitter_m3u8(url, file):
    res = r.get(url)
    p = re.compile('/(\d+x\d+)/')
    max_resol = 0
    link = ''
    for line in res.text.split('\n'):
        if not line.startswith('#') and line != '':
            m = p.search(line)
            w, h = map(int, m.group(1).split('x'))
            resol = w * h
            if resol > max_resol:
                link = line
                max_resol = resol
    return download_m3u8('https://video.twimg.com' + link, file)

def download_m3u8(url, file):
    res = r.get(url)
    for line in res.text.split('\n'):
        if not line.startswith('#') and line != '':
            link = 'https://video.twimg.com' + line
            stream = r.get(link, stream=True)
            with open(file, 'ab') as f:
                for chunk in stream.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
    return True