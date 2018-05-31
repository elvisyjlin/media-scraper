# Media Scraper

`media-scraper` scrapes all photos and videos in a web page. 
It supports general-purpose scraping as well as SNS-specific scraping. 


##### General-purpose Scraping

The general media scraper scrapes and downloads all photos and videos 
in all links `<a/>`, images `<img/>` and videos `<video/>` of a web page. 


##### SNS-specific

Currently there are **Instagram** scraper and **Twitter** scraper, 
which crawl all posts of a given user and download media in a proper way for each SNS. 


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


### Media Scraper


#### General

```python
import mediascraper
scraper = mediascrapers.MediaScraper()
scraper.connect(URL)
scraper.scrape(path=SAVE_PATH)
```


#### Social Network Services

```python
import mediascraper
scraper = mediascrapers.InstagramScraper()
# scraper = mediascrapers.TwitterScraper()
scraper.username(USERNAME)
scraper.scrape(path=SAVE_PATH)
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
Please see [instagramer.py](https://github.com/elvisyjlin/tumblrer), which works well for downloading all media form Instagram.


### Twitter

For some reasons, Twitter utilizes blob url for videos, which is not supported by `media-scraper` currently. 
I'm still working on this problem.