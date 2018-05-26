query_hash = '42323d64886122307be10013ad2dcc44'  # query shorcode pages
# query_hash = '9ca88e465c3f866a76f7adee3871bdd8'  # query `{"data":{"viewer":null,"user":null},"status":"ok"}`
userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'

def getSharedData(username):
    import requests
    import re
    import json
    import time
    from bs4 import BeautifulSoup
    headers = {
        'User-Agent': userAgent
    }
    
    success = False
    while not success:
        try:
            # print('Get', 'https://www.instagram.com/' + username, 'with',  headers)
            res = requests.get('https://www.instagram.com/' + username, headers=headers, verify=False)
            # print(res)
            while res.status_code != 200:
                print('Got response', res.status_code)
                print('Sleep for 1 hour...')
                time.sleep(1 * 60 * 60)
                res = requests.get('https://www.instagram.com/' + username, headers=headers, verify=False)

            content = res.text
            soup = BeautifulSoup(content, 'html.parser')
            for script in soup.find_all('script'):
                p = re.compile('window._sharedData = (.*?);$')  # $ specifies the end of the string
                m = p.match(script.string)
                if m is not None:
                    break
            sharedData = json.loads(m.groups()[0])
            success = True
        except Exception as e:
            with open('error', 'w', 'utf-8') as f:
                f.write(content)
            print(e)
            print('content', content)
    return sharedData

def get_x_instagram_gis(rhx_gis, url):
    import hashlib
    vals = rhx_gis + ':' + url.split('variables=')[1]
    m = hashlib.md5()
    m.update(vals.encode())
    return m.hexdigest()

def getFirstPage(username):
    sharedData = getSharedData(username)
    csrf_token = sharedData['config']['csrf_token']
    rhx_gis = sharedData['rhx_gis']

    user = sharedData['entry_data']['ProfilePage'][0]['graphql']['user']
    is_private = user['is_private']
    user_id = user['id']
    profile_pic_url = user['profile_pic_url']
    profile_pic_url_hd = user['profile_pic_url_hd']

    edge_owner_to_timeline_media = user['edge_owner_to_timeline_media']
    end_cursor = edge_owner_to_timeline_media['page_info']['end_cursor']
    has_next_page = edge_owner_to_timeline_media['page_info']['has_next_page']
    count = edge_owner_to_timeline_media['count']
    edges = edge_owner_to_timeline_media['edges']

    # print('Searching edges...')
    tasks = []
    for edge in edges:
        node = edge['node']
        typename = node['__typename'] # 'GraphImage', 'GraphVideo', 'GraphSidecar'
        node_id = node['id']
        display_url = node['display_url']
        shortcode = node['shortcode']
        # print(shortcode, typename, display_url)
        tasks.extend(parse_node(retrieve_node_from_shortcode(shortcode)))

    return tasks, end_cursor, has_next_page, len(edges), user_id, rhx_gis, csrf_token

def getFollowingPage(query_hash, user_id, after, rhx_gis, csrf_token):
    import requests
    import json
    import time
    first = 12

    url = 'https://www.instagram.com/graphql/query/?query_hash={}&variables={{"id":"{}","first":{},"after":"{}"}}'.format(query_hash, user_id, first, after)

    headers = {
        'User-Agent': userAgent, 
        'X-Instagram-GIS': get_x_instagram_gis(rhx_gis, url)
    }
    cookies = {
        'csrf_token': csrf_token
    }
    success = False
    while not success:
        try:
            res = requests.get(url, headers=headers, cookies=cookies, verify=False)
            edge_owner_to_timeline_media = json.loads(res.text)['data']['user']['edge_owner_to_timeline_media']
            success = True
        except Exception as e:
            print(e)
            with open('error', 'w', encoding='utf-8') as f:
                f.write(res.text)
            print('Sleep for 1 hour...')
            time.sleep(1 * 60 * 60)
    count = edge_owner_to_timeline_media['count']
    end_cursor = edge_owner_to_timeline_media['page_info']['end_cursor']
    has_next_page = edge_owner_to_timeline_media['page_info']['has_next_page']
    edges = edge_owner_to_timeline_media['edges']
    
    tasks = []
    for edge in edges:
        node = edge['node']
        typename = node['__typename'] # 'GraphImage', 'GraphVideo', 'GraphSidecar'
        node_id = node['id']
        display_url = node['display_url']
        shortcode = node['shortcode']
        # print(shortcode, typename, display_url)
        tasks.extend(parse_node(retrieve_node_from_shortcode(shortcode)))

    return tasks, end_cursor, has_next_page, len(edges)

def largest_image_url(resources):
    return max(resources, key=lambda x: x['config_height']*x['config_width'])['src']

def node_name(node):
    return '{}.{}'.format(node['id'], node['shortcode'])

def parse_node(node, name=''):
    tasks = []

    if name == '':
        name = node_name(node)
    else:
        name += '.' + node_name(node)

    # import json
    # with open('tmp', 'w') as f:
    #     f.write(json.dumps(node))
    # print(node.keys())
    # print(node['__typename'])
    # print(node['display_url'])
    # print(node['thumbnail_resources'])
    
    display_resources = node['display_resources']
    # find the highest resolution image
    url = largest_image_url(display_resources)
    # download(url, path=save_path, rename=name, replace=False)
    tasks.append((url, name + '.' + url.rsplit('.', 1)[1]))

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
        tasks.append((url, name + '.' + url.rsplit('.', 1)[1]))
    else:
        print('Error: unsupported typename "{}".'.format(typename))

    return tasks

# Go into the page for a certain post and get the node information
def retrieve_node_from_shortcode(shortcode):
    import requests
    import json
    import time
    url = 'https://www.instagram.com/p/{}/?__a=1'.format(shortcode)
    # print(url)
    headers = {
        'User-Agent': userAgent
    }
    success = False
    while not success:
        try:
            res = requests.get(url, headers=headers, verify=False)
            node = json.loads(res.text)['graphql']['shortcode_media']
            success = True
        except Exception as e:
            print(e)
            print('Sleep for 1 hour...')
            time.sleep(1 * 60 * 60)
    return node