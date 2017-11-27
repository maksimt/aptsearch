#!/bin/bash

# Remove output file if exists:
[ -e aptscrape/good_stuff.json ] && rm aptscrape/good_stuff.json

cd aptscrape
scrapy crawl scrapeapts -o good_stuff.json

cd ..
python email_me.py
