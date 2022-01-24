# Spider 2
# ArticleScraper.py which scrape article headlies and bodies
# imports
import MySQLdb
import unicodedata
import scrapy
from scrapy.http import Request
from TRTWorld.items import TrtworldItem
import json

class ArticlescraperSpider(scrapy.Spider):
    name = 'ArticleScraper'
    allowed_domains = ['trtworld.com']
    start_urls = ['http://trtworld.com/']
    sql_cxn = 'this is a mysql connector'


    def start_requests(self):
        headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        
        self.sql_cxn = MySQLdb.connect('localhost','root','gwailo98(*','predictor')
        cursor = self.sql_cxn.cursor()

        # Open the JSON file which contains article links
        for i in ['article_links1.json', 'article_links.json']: 
            with open(i) as json_file:
                data=json.load(json_file)
           
                for p in data:
                    print('URL: ' + p['article_url'])
                    if(isinstance(p['article_date'], list)):
                        p_date=p['article_date'][0]
                    else:
                        p_date=p['article_date']

                    # Request to get the HTML content
                    request=Request(p['article_url'], headers=headers, cookies={'store_language':'en'}, callback=self.parse_article_page, meta={"date":p_date, "cursor":cursor})
                    yield request
        self.sql_cxn.commit()
        self.sql_cxn.close()

    def parse_article_page(self,response):
        cursor=response.meta.get("cursor")
        item=TrtworldItem()
        item['article_date']=response.meta.get("date")
        item['article_url']=response.request.url

        # Extracts the article_title and stores in scrapy item
        a_title=""
        for p in response.xpath('//h1[@class="article-title"]/text()').extract():
            a_title=a_title+p
        item['article_title']=self.clean_string(a_title)

        # Extracts the article_description and stores in scrapy item
        a_desc=""
        for p in response.xpath('//h3[@class="article-description "]/text()').extract():
            a_desc=a_desc+p
        item['article_description']= self.clean_string(a_desc)

        # Extracts the article_body in <p> elements
        a_body=""
        for p in response.xpath('//div[@class="contentBox bg-w noMedia"]//p/text()').extract():
            a_body=a_body+p
        for p in response.xpath('//div[@class="contentBox bg-w hasMedia"]//p/text()').extract():
            a_body=a_body+p
        item['article_body']= self.clean_string(a_body)

        insert_query="INSERT INTO all_articles (article_date, article_url, full_text, article_title) VALUES (%s, %s, %s, %s)"
        query_data = (item['article_date'], item['article_url'], item['article_body'], item['article_title'])
        cursor.execute(insert_query, query_data)

        yield(item)

    def clean_string(self, input_string):
        return unicodedata.normalize('NFKD', input_string).encode('ascii', 'ignore').decode('ascii').replace("\n", " ")