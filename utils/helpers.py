import requests

def log(msg, file='log.txt'):
    print(msg)
    with open(file, 'a') as f:
        f.write(msg + '\n')
        
def get_imgur(url):
    '''
    Returns an image url (jpg, png, gif, ...) of the given Imgur url.
    '''
    
    assert 'imgur.com/' in url, 'Error occurs when parsing url [{}]'.format(url)
    
    IMGUR_URL = 'https://i.imgur.com/{}.{}'
    IMGUR_JPG = 'https://i.imgur.com/{}.jpg'
    
    img_id = url.rsplit('/', 1)[1]
    res = requests.head(IMGUR_JPG.format(img_id))
    
    if int(res.headers['Content-Length']) == 0:
        return None
    
    try:
        content_type = res.headers['Content-Type']
    except Exception as e:
        print(IMGUR_JPG.format(img_id))
        print(res.headers)
        raise e
        
    ext = content_type.split('/')[1]
    ext = 'jpg' if ext == 'jpeg' else ext
    
    return IMGUR_URL.format(img_id, ext)
    

def get_gfycat(url):
    '''
    Returns an mp4 url and a webm url of the given Gfycat url.
    '''
    
    assert 'gfycat.com/' in url, 'Error occurs when parsing url [{}]'.format(url)
    
    GFYCAT_MP4  = 'https://giant.gfycat.com/{}.mp4'
    GFYCAT_WEBM = 'https://giant.gfycat.com/{}.webm'
    
    name = url.rsplit('/', 1)[1]
    
    return [GFYCAT_MP4.format(name), 
            GFYCAT_WEBM.format(name)]