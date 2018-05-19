# Tumblrer


## Requirement

```bash
pip3 install -r requirements
```


## Get Started

##### Crawl all media in a page

```bash
python3 tumblrer.py <url_1> <url_2> <...> --save_path=<folder> <--early_stop>
```

The argument `--early_stop` specifies that Tumblrer stops if it meets an existing media (in your download folder).

The crawled media will be stored as the following structure.

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