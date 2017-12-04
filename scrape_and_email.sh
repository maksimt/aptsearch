#!/bin/sh
export PATH="/Users/Leo/anaconda3/bin:$PATH"

# Remove output file if exists:
[ -e /Users/Leo/projects/aptsearch/aptscrape/good_stuff.json ] && rm /Users/Leo/projects/aptsearch/aptscrape/good_stuff.json

cd /Users/Leo/projects/aptsearch/aptscrape
scrapy crawl scrapeapts -o /Users/Leo/projects/aptsearch/aptscrape/good_stuff.json

cd /Users/Leo/projects/aptsearch
python /Users/Leo/projects/aptsearch/email_me.py
