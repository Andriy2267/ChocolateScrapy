import scrapy
from urllib.parse import urlencode
from chocolatescraper.items import ChocolateProduct
from chocolatescraper.itemloader import ChocolateProductLoader

API_KEY = '9e693e26-5d43-46b2-92e4-6a7a9c92ec68'

def get_proxy_url(url):
    payload = { 'api_key': API_KEY, 'url': url }
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

class ChocolatespiderSpider(scrapy.Spider):
    name = "chocolatespider"
    allowed_domains = ["chocolate.co.uk"]
    # start_urls = ["https://www.chocolate.co.uk/collections/all"]

    def start_requests(self):
        start_url = "https://www.chocolate.co.uk/collections/all"
        yield scrapy.Request(url=get_proxy_url(start_url), callback=self.parse)

    def parse(self, response):

        products = response.css("product-item")
        
        for product in products:
            chocolate = ChocolateProductLoader(item=ChocolateProduct(), selector=product)
            chocolate.add_css('name', 'a.product-item-meta__title::text'),
            chocolate.add_css('price', 'span.price', re='<span class="price">\n              <span class="visually-hidden">Sale price</span>(.*)</span>'),
            chocolate.add_css('url', "div.product-item-meta a::attr(href)")
            
            yield chocolate.load_item()
        
        next_page = response.css(".heading--small::attr(href)").get()

        if next_page is not None:
            next_page_url = "https://www.chocolate.co.uk" + next_page
            yield response.follow(url=get_proxy_url(next_page_url), callback=self.parse)
        
        

