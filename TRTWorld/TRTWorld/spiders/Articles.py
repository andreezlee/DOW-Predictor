# Spider 1 
# Articles.py which scrape article links

# imports
from os.path import exists
import math
import pickle
from datetime import date, timedelta
import scrapy
from scrapy.http import Request
from TRTWorld.items import TrtworldItem

class ArticlesSpider(scrapy.Spider):
    name = 'Articles'
    allowed_domains = ['trtworld.com']
    start_urls = ['http://trtworld.com/']
    article_set = set()
    reached_end = False

    def start_requests(self):

        """
        # This website cannot display more recent search results properly
        # Hardcoded URL that contains bounded dates
        url="https://www.trtworld.com/search?query=us&order=_score&date=custom&startDate={}&endDate={}&regions%5B%5D=americas&sections%5B%5D=culture&sections%5B%5D=business&sections%5B%5D=life&sections%5B%5D=sport&type=news"
        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

        start_date = date(2016, 4, 1)
        end_date = date.today()
        delta = end_date - start_date

        link_urls = [url.format((start_date + timedelta(days=i)).strftime("%Y-%m-%d"),(start_date + timedelta(days=i)).strftime("%Y-%m-%d")) for i in range(delta.days + 1)]
        link_dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]
        assert len(link_urls) == len(link_dates)

        # Loops through all pages to get the article links
        for i in range(len(link_urls)):
            link_url = link_urls[i]

            # Request to get the HTML content
            request=Request(link_url, headers=headers, cookies={'store_language':'en'}, callback=self.parse_main_pages)
            yield request
        with open('all_articles.pickle', 'wb') as f:
            pickle.dump(self.article_set, f)
        """

        if exists('all_articles.pickle'):
            with open('all_articles.pickle', 'rb') as f:
                self.article_set = pickle.load(f)

        url="https://www.trtworld.com/americas?page={}"
        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

        link_urls = [url.format(i) for i in range(1000)]

        # Loops through all pages to get the article links
        for i in range(len(link_urls)):
            link_url = link_urls[i]

            # Request to get the HTML content
            request=Request(link_url, headers=headers, cookies={'store_language':'en'}, callback=self.parse_main_pages)
            yield request
        with open('all_articles.pickle', 'wb') as f:
            pickle.dump(self.article_set, f)


    def parse_main_pages(self,response):
        item=TrtworldItem()
        # Gets HTML content where the article links and dates are stored
        content1=response.xpath('//div[@id="items"]//div[@class="caption"]').xpath('.//a')
        content2=response.xpath('//div[@id="items"]//div[@class="article-meta"]').xpath('.//a')
        print('# Links: {}'.format(len(content1)))
        print('# Dates: {}'.format(len(content2)))
        assert len(content1) == 2 * len(content2)

        # Loops up article links in HTML 'content'
        for i in range(len(content1)):
            article_link = content1[i]
            article_date = content2[math.floor(i/2)]

            # Extracts the href info of the link to store in scrapy item
            full_url = "https://www.trtworld.com"+article_link.xpath('.//@href').extract_first()
            if full_url not in self.article_set:
                self.article_set.add(full_url)
                item['article_url'] = full_url
                item['article_date'] = self.parse_dates(article_date.xpath('.//text()').extract()[0])
                yield(item)

    def parse_dates(self, date_string):
        words = date_string.split()
        if 'day' in date_string:
            return (date.today() - timedelta(int(words[0]))).strftime("%d %b %Y")
        if 'hour' in date_string:
            return date.today().strftime("%d %b %Y")
        return date_string
