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
python3 -m mediascraper.instagram [USER ID 1] [USER ID 2] ...
```

The media will be stored in the folder `download/instagram`.

```bash
python3 -m mediascraper.twitter [USER ID 1] [USER ID 2] ...
```

The media will be stored in the folder `download/twitter`.


### Login with Credentials

If you want to scrape a user's media with your account, 
just rename `credentials.json.example` to `credentials.json` and fill in your username and password. 


## To Import


### Media Scraper


#### General

```python
import mediascraper
scraper = mediascrapers.MediaScraper()
scraper.connect(WEB_PAGE)
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
