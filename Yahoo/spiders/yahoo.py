import  scrapy
from ..items import YahooItem
from scrapy_splash import SplashRequest
from scrapy.http import FormRequest
import logging
import re

class YahooSpider(scrapy.Spider):
    name = 'yahoo'
    start_url='https://tw.buy.yahoo.com/search/product'

    def start_requests(self):
        queryStringList=[
        {
            'p':'電風扇'
        },
        # {
        #     'p':'爬蟲',
        # },
        # {
        #     'p':'電腦',
        # }
        ]
        for queryString in queryStringList:
            yield FormRequest(url=self.start_url,method='GET',formdata=queryString,callback=self.detail_request,dont_filter=True)
    #得到js原碼
    def detail_request(self,response):

                                   #url                    #callback                                                         #網址很像不要過濾
        yield SplashRequest(response.request.url,self.deep_request,meta={'url':response.request.url},endpoint='render.html',dont_filter=True)
    #得到渲染後的html
    def deep_request(self,response):
        lua_script = """
        function main(splash)
        local num_scrolls = 10
        local scroll_delay = 1

        local scroll_to = splash:jsfunc("window.scrollTo")
        local get_body_height = splash:jsfunc(
            "function() {return document.body.scrollHeight;}"
        )
        assert(splash:go(splash.args.url))
        for _ = 1, num_scrolls do
            local height = get_body_height()
            for i = 1, 10 do
                scroll_to(0, height * i/10)
                splash:wait(scroll_delay/10)
            end
        end        
        return splash:html()
        end
        """
        url=response.meta.get('url')
        amount=response.xpath('//*[@id="isoredux-root"]/div[2]/div/div[2]/div/div[1]/span/text()').get().split()[0]
        page=int(int(amount)/60)+1
        for page in range(1,page):
            yield SplashRequest(url+"&pg="+str(page),endpoint='execute',args={"lua_source":lua_script,"url":url+"&pg="+str(page)},dont_filter=True)
            
    def parse(self,response):
        r_list=response.xpath('//*[@id="isoredux-root"]/div[2]/div/div[2]/div/div[2]/ul/li[contains(@class,"BaseGridItem__grid___2wuJ7")]')
        for i in r_list:
            item=YahooItem()
            replenish=i.xpath('.//span[@class="BaseGridItem__statusMask___1ZrC7"]/text()').get()
            if replenish:
                break
            item['name']=i.xpath('.//span[@class="BaseGridItem__itemInfo___3E5Bx"]/span/text()').get()
            item['price']=i.xpath('.//em/text()').get()
            yield item