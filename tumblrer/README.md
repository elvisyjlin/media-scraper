# Tumblrer, Instagramer, Redditer


## Requirement

```bash
pip3 install -r requirements
```


## Get Started

The usages of `tumblrer`, `instagramer`, and `redditer` are all the same. 
And the `instagramer` is implemented following the latest Instagram query API. 

Here we take `tumblrer` as an example: 


##### Crawl all media in a page

```bash
python3 tumblrer.py <url_1/file_1> <url_2/file_2> <...> --save_path=<folder> <--early_stop>
```

`tumblrer` will crawl all urls in the arguments. If it is a file ending with `.txt`, it views each line in the file as an url and download media from it. 

The argument `--early_stop` specifies that Tumblrer stops if it meets an existing media (in your download folder). 

For `tumblrer`, the crawled media will be stored as the following structure: 

```
 - <folder>
   - site1
     - photo
       - img1
       - img2
       - ...
     - video
       - vid1
       - vid2
   - site2
   - ...
```

For `instagramer` and `redditer`, they will be stored as: 

```
 - <folder>
   - username1 or subreddit1
     - media1
     - media2
     - ...
   - username2 or subreddit2
   - ...
```


##### Utilize Tumblr in your program

```python
import tumblrer
tumblrer.path(save_path)
tumblrer.crawl(urls)  # urls should be a list of urls
```

Note that Tumblrer skips existing files automatically.


##### Show the statistics of downloaded media

```bash
python3 stat.py
```
