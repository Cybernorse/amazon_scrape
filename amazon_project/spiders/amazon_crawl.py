import scrapy 
import re


class amazon_scrape(scrapy.Spider):
    name="amz"
    # rotate_user_agent=True
    allowed_domains=['www.amazon.com']

    def start_requests(self):

        start_urls=[
            'https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/ref=zg_bs_nav_0',
        ]

        for i in start_urls:
            # token, agent = cfscrape.get_tokens(i,'Mediapartners-Google')
            yield scrapy.Request(url=i,callback=self.parse)

    def parse(self,response):
        dept=response.xpath('//div[@id="zg-left-col"]/ ul[@id="zg_browseRoot"]/ ul //a/@href').getall()
        for i in dept:
            if i:
                yield response.follow(i,self.scrape_item)

    def scrape_item(self,response):
        items_link=response.xpath('//span[@class="aok-inline-block zg-item"]/ a[@class="a-link-normal"]/ @href').getall()
        item_title=response.xpath('//div[@class="p13n-sc-truncate p13n-sc-line-clamp-2"]/text()').getall()
        item_price=response.xpath('//span[@class="a-size-base a-color-price"]').getall()
        item_image_url=response.xpath('//div[@class="a-section a-spacing-small"]//img/@src').getall()
        item_rating=response.xpath('//div[@class="a-icon-row a-spacing-none"]/ a[@class="a-link-normal"]/ @title').getall()
        total_reviews=response.xpath('//a[@class="a-size-small a-link-normal"]/text()').getall()
        category_directs=response.xpath('//li[@class="zg_browseUp"]/ a/text()').getall()+response.xpath('//span[@class="zg_selected"]/text()').getall()
    
        zipped=zip(items_link,item_title,item_price,item_image_url,item_rating,total_reviews)
        for i in zipped:
            if i:
                pattern=re.findall(r'\$\d+?\.\d+',i[2])
                yield {
                    'ASIN':[i.split('?')[0] for i in i[0].split('/') if '?' in i][0],
                    'category':'/'.join(category_directs),
                    'links':'https://www.amazon.com'+i[0],
                    'title':i[1],
                    'price':' '.join(pattern),
                    'image url':i[3],
                    'rating':i[4],
                    'No of reviews':i[5],
                }

        next_link=response.xpath('//ul[@class="a-pagination"] //a/@href').getall()
        for i in next_link:
            if i:
                yield response.follow(i,self.scrape_item)

        sub_dept=response.xpath('//div[@id="zg-left-col"]/ ul[@id="zg_browseRoot"]/ ul //a/@href').getall()
        for i in sub_dept:
            if i:
                yield response.follow(i,self.scrape_item)





    # def get_items(self,response):
    #     title=response.xpath('//*[@id="productTitle"]/text()').getall()
    #     price=response.xpath('//*[@id="priceblock_ourprice"]/text()').getall()
    #     asin=response.xpath('/html/body/div[2]/div[1]/div[7]/div[29]/div/div/div/div/div/div/div[1]/div/div/table/tbody/tr[4]/td/text()').getall()

    #     yield{
    #         'title':title,
    #         'price':price,
    #     }
