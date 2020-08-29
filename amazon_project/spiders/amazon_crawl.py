import scrapy 
import re

#   create a folder "amazon_project" and download the project in that directory

class amazon_scrape(scrapy.Spider):
#   name of the spider to use when running spider and exporting the csv ( scrapy crawl amz -o amazon_data.csv )
    name="amz"
#   spider will not go out of this domain.
    allowed_domains=['www.amazon.com']
    
#   this method is used to start the requests from the given url --> start_urls 
    def start_requests(self):
        start_urls=[
            'https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/ref=zg_bs_nav_0',
        ]

        for i in start_urls:
            yield scrapy.Request(url=i,callback=self.parse)
            
#   this method will accept response from the start_requests method and will get the categories links from the first page get the response 
#   and send it to the scrape_item method 
    def parse(self,response):
        dept=response.xpath('//div[@id="zg-left-col"]/ ul[@id="zg_browseRoot"]/ ul //a/@href').getall()
        for i in dept:
            if i:
                yield response.follow(i,self.scrape_item)

#   this mehtod is used to scrape data 
    def scrape_item(self,response):
#       following is the data to be extracted from each of the item
        items_link=response.xpath('//span[@class="aok-inline-block zg-item"]/ a[@class="a-link-normal"]/ @href').getall()
        item_title=response.xpath('//div[@class="p13n-sc-truncate p13n-sc-line-clamp-2"]/text()').getall()
        item_price=response.xpath('//span[@class="a-size-base a-color-price"]').getall()
        item_image_url=response.xpath('//div[@class="a-section a-spacing-small"]//img/@src').getall()
        item_rating=response.xpath('//div[@class="a-icon-row a-spacing-none"]/ a[@class="a-link-normal"]/ @title').getall()
        total_reviews=response.xpath('//a[@class="a-size-small a-link-normal"]/text()').getall()
        category_directs=response.xpath('//li[@class="zg_browseUp"]/ a/text()').getall()+response.xpath('//span[@class="zg_selected"]/text()').getall()
        
#       preparing the data to be written to the csv file, we are yielding a dictionary in our case.
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
                
#       getting to the next page of the same category if any and calling the generator again to scrape the data from here as well this will go as long as there
#       are next links.
        next_link=response.xpath('//ul[@class="a-pagination"] //a/@href').getall()
        for i in next_link:
            if i:
                yield response.follow(i,self.scrape_item)
              
#       once done with the all items in the current page other categories links will be extracted and scrape_item generator will be called again 
#       to perform above operations again, this will go on as long as there are categories available to crawl.      
        sub_dept=response.xpath('//div[@id="zg-left-col"]/ ul[@id="zg_browseRoot"]/ ul //a/@href').getall()
        for i in sub_dept:
            if i:
                yield response.follow(i,self.scrape_item)


