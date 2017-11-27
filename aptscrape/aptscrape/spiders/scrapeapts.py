# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
import time
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
import sys
import traceback

geolocator = Nominatim()
work_loc = geolocator.geocode("3500 Deer Creek Road, Palo Alto")
work_lat_long = (work_loc.latitude, work_loc.longitude)

class CraigslistItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    hood = scrapy.Field()
    listing_url = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    miles_from_work = scrapy.Field()
    exception = scrapy.Field()
    contact_email = scrapy.Field()


class ScrapecontentsSpider(CrawlSpider):
    name = 'scrapeapts'

    allowed_domains = ['sfbay.craigslist.org']
    start_urls = ['https://sfbay.craigslist.org/search/apa?']

    rules = (
        Rule(link_extractor=LinkExtractor(allow=r'sfbay.craigslist.org/search/apa.*',
                                          deny=([r'.*format\=rss.*',
                                                 r'.*sort=.*',
                                                 r'.*?s=.*'])),
             callback='parse_content_list',
             follow=True),
    )

    def parse_content_list(self, response):
        print('\n\n')
        self.logger.info('NOW CRAWLING THE FOLLOWING PAGE: {url}'.format(url=response.url))
        contents = response.xpath("//p[@class='result-info']")
        
        interest_list = []

        for content in contents:
            try:
                item = CraigslistItem()
                meta_xpath = "span[@class='result-meta']/"
                item['title'] = content.xpath("a[@class='result-title hdrlnk']/text()").extract_first()
                item['price'] = content.xpath(meta_xpath+"span[@class='result-price']/text()").extract_first().replace('$','')
                item['hood'] = content.xpath(meta_xpath+"span[@class='result-hood']/text()").extract_first().replace('(','').replace(')','').strip()
                item['listing_url'] = content.xpath("a/@href").extract()[0]

                listing_html = requests.get(item['listing_url']).text
                soup = BeautifulSoup(listing_html, 'lxml')
                item['latitude'] = soup.find("div", {"class":"viewposting"}).get("data-latitude")
                item['longitude'] = soup.find("div", {"class":"viewposting"}).get("data-longitude")
                item['miles_from_work'] = vincenty(work_lat_long, (item['latitude'], item['longitude'])).miles
                
                try:
                    reply_ext = soup.find("span", {"class":"replylink"}).find("a").get("href")
                    contact_url = 'https://sfbay.craigslist.org' + reply_ext
                    contact_html = requests.get(contact_url).text
                    contact_soup = BeautifulSoup(contact_html, 'lxml')
                    item['contact_email'] = contact_soup.find("p", {"class":"reply-email-address"}).find("a").get("href").replace('mailto:','').split('?')[0]
                except:
                    print("\n\CAPTCHA'D! You are a robot and can't prove otherwise :(")

                if self.meets_conditions(item=item):
                    interest_list.append(item)
            
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                item['exception'] = e
            
            print('\n')
            print(item)
            print('\n')
            time.sleep(1)

        return interest_list

    def meets_conditions(self, item):
        if int(item['price']) < 3000 and float(item['miles_from_work']) < 15:
            print('\nFOUND ONE!')
            return True
        else:
            return False

