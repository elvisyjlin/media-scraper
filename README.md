# Media Scraper

`media-scraper` scrapes all photos and videos in a web page. 
It supports general-purpose scraping as well as SNS-specific scraping. 

`media-scraper` utilizes the web driver to simulate a user browsing web pages. 
With the web driver, sessions and cookies easily can be handled easily but it works slightly slowly.
On the other hand, I'm currently working on the migration of another [repository](https://github.com/elvisyjlin/tumblrer), 
which crawls media only by HTTP requests, to this repository. See [here](https://github.com/elvisyjlin/media-scraper/tree/master/tumblrer).


##### General-purpose Scraping

The general media scraper scrapes and downloads all photos and videos 
in all links `<a/>`, images `<img/>` and videos `<video/>` of a web page. 


##### SNS-specific

Currently there are **Instagram** scraper and **Twitter** scraper, 
which crawl all posts of a given user and download media in a proper way for each SNS. 


## Updates

Current, `media-scraper` is merged to contain two methods of scraping: _by request_ and _by browser_.


### Usage

```bash
python3 m-scraper.py rq instagram [USERNAME1 USERNAME2 ...] [-e] [-s SAVE_PATH] [-c CRED_FILE]
python3 m-scraper.py rq tumblr [SITE1 SITE2 ...] [-e] [-s SAVE_PATH] [-c CRED_FILE]
python3 m-scraper.py rq reddit [SUBREDDIT1 SUBREDDIT2 ...] [-e] [-s SAVE_PATH] [-c CRED_FILE]
python3 m-scraper.py rq pixiv [USERID1 USERID2 ...] [-e] [-s SAVE_PATH] [-c CRED_FILE]
python3 m-scraper.py rq tiktok [USERID1 USERID2 ...] [-e] [-s SAVE_PATH] [-c CRED_FILE]
```

If you'd like to download with your own credentials, i.e. logging in your account, please put your username and password in `credentials.json` and run `m-scraper.py` with `-c credentials.json`.

```bash
mv ./credentials.json.example ./credentials.json
vim ./credentials.json
```

Note that pixiv requires a user login to view all illustrations and mangas. If you scrape pixiv without logging in, you'll get only some of them.

For scraping TikTok videos, you'll need to get the user id first. Go to the user page in your TikTok App, share it via link, paste it in a browser, and you'll see the user id in the url bar. E.g. user id of _TikTok_ is 107955. However, `m-scraper` here fetch video list via TikTok shared content, it contains most of the videos but not all of them. I'll dig into the mobile App API in the future.


## Installation

Clone the `media-scraper` git repository.

```bash
git clone https://github.com/elvisyjlin/media-scraper.git
cd media-scraper
```

Install Python 3 (at least 3.5) and get all dependencies.

```bash
pip3 install -r requirements.txt
```


#### Web Driver

`media-scraper` loads the content of a web page by web driver (PhantomJS). 
The needed web driver will be downloaded automatically when it is used.

If you meet permission error, for example,  

```python
selenium.common.exceptions.WebDriverException: Message: 'phantomjs' executable may have wrong permissions.
```

Please set the web driver to `777` for convenience.

```bash
chmod 777 webdriver/phantomjsdriver_2.1.1_win32/phantomjs.exe
chmod 777 webdriver/phantomjsdriver_2.1.1_mac64/phantomjs
chmod 777 webdriver/phantomjsdriver_2.1.1_linux64/phantomjs
```


## To Scrape

```bash
python3 -m mediascraper.general [WEB PAGE 1] [WEB PAGE 2] ...
```

The media will be stored in the folder `download/general`.

```bash
python3 -m mediascraper.instagram [USER NAME 1] [USER NAME 2] ...
```

The media will be stored in the folder `download/instagram`.

```bash
python3 -m mediascraper.twitter [USER NAME 1] [USER NAME 2] ...
```

The media will be stored in the folder `download/twitter`.


For example, to scrape [`Twitter`](https://twitter.com/Twitter)

```bash
python3 -m mediascraper.twitter Twitter
```


### Login with Credentials

If you want to scrape a user's media with your account, 
just rename `credentials.json.example` to `credentials.json` and fill in your username and password. 


## To Import

It is easy to import `media-scraper` into your scripts and make use of it.
Please refer to the [example code](https://github.com/elvisyjlin/media-scraper/tree/master/mediascraper) for more details.


### Media Scraper

```
python3 -m mediascraper.general [URL1 URL2 ...]
python3 -m mediascraper.instagram [USERNAME1 USERNAME2 ...]
python3 -m mediascraper.twitter [USERNAME1 USERNAME2 ...]
```


### Parameters of Scraper

Parameter | Description | Default Value
--- | --- | ---
scroll_pause | the pause interval when scrolling| `0.5` (seconds)
mode | `'silent'`, `normal'` or `'verbose'` | `'normal'`
debug | prints debugging messages if `True` | `False`


### Connect Methods of Scraper

Scraper | Methods
--- | ---
MediaScraper | `connect(URL)`
InstagramScraper | `username(USERNAME)`
TwitterScraper | `username(USERNAME)`


## Note


### Instagram

Instagram changed API 3 times this year (2018), so the query API in `media-scraper` is out-of-date. 
Please see [`instagramer.py`](https://github.com/elvisyjlin/media-scraper/blob/master/m_scraper/rq/instagramer.py), which works well for downloading all media form Instagram.
The instruction is [here](https://github.com/elvisyjlin/media-scraper#usage).


### Twitter [Solved]

For some reasons, Twitter utilizes blob url for videos, which is not supported by `media-scraper` currently. 
I'm still working on this problem.

06/07/2018 Update: It supports downloading videos in Twitter now!
