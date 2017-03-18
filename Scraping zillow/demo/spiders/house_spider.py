# -*- coding: utf-8 
import re
import json
import scrapy
from scrapy import Spider
from scrapy.selector import Selector
from demo.items import ZillowItem
import geocoder 

g = geocoder.google([37.78989,-122.54737], method='reverse')
postal_code = g.postal

QUERY  = "/san-francisco-ca"

class TruliaSpider(Spider):
    name = 'property'
    allowed_urls = ["https://www.zillow.com"]
    start_urls = ["https://www.zillow.com/homes"+ QUERY+"-"+ postal_code]
    

    def getting_the_next_page(self,response):
    
        try: 
        #to get the last page and make our code robust 
            next_page_number = int(len(response.xpath('//*[@id="search-pagination-wrapper"]/ol/li')))
            print (next_page_number)
            return next_page_number
    
        except indexError:
        #if there is no page number in there
        #get the reason of the error too
            reasons = response.xpath('//p[@class = "text-lead"]/text()').extract()
        #if the page number does not return go back to page 0
            if reason in reasons[0]:
                logging.log(logging.DEBUG, 'no result on the page' + response.url)
                return 0
            else:
        #or else we conclude that there is only one page
                return 1
    def parse(self,response):
        #apply the function to get last page number and get response from all the pages
        next_page_number = self.getting_the_next_page(response)
        if next_page_number < 1:
            return 
        else:
            page_urls = [response.url + str(page_number) + "_p/" for page_number in range(1 , next_page_number)]
            for page_url in page_urls:
                print (page_url)
                yield scrapy.Request(page_url,
                    callback = self.parse_listing_return_page)
                
    def parse_listing_return_page(self,response):
        #lets get the href of each listing in each page.
        
        dra = response.xpath('//div//li//article//a/@href').extract()
        for href in ["https://www.zillow.com"+x for x in dra if not 'htm?' in x]:
            url = response.urljoin(href)
            
            yield scrapy.Request(url,
                callback = self.parse_final)
    def parse_final(self,response):
        #now we have got the response from other page.
        # lets get the data we want.
        item = ZillowItem()

        item['photo_address'] = response.xpath('//div//img//@href').extract()
        item['price'] = response.xpath('//*[@id="home-value-wrapper"]//div//div/span/text()').extract()
        item['description'] = response.xpath('//section//div//ul//li/text()').extract()


        
        ##############################################################################

        item['url'] = response.url
        yield item