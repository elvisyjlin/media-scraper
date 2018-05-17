# Tumblrer


## Requirement

```bash
pip3 install -r requirements
```


## Get Started

##### Crawl all media in a page

```bash
python3 tumblrer.py <url_1> <url_2> <...> --save_path=<folder>
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