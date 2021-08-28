import scrapy
from scrapy.http import HtmlResponse
from lreoymerlinru.items import LreoymerlinruItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, category):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/catalogue/{category}/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa-pagination-item='right']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        object_links = response.xpath("//section[contains(@class, 'plp')]/div[contains(@class, 'largeCard')]/div[contains(@class, 'largeCard')]/a")
        for link in object_links:
            yield response.follow(link, callback=self.item_parse)

    def item_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=LreoymerlinruItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('url', 'response.url')
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('photos', "//picture[@slot='pictures']/source[@media=' only screen and (min-width: 1024px)']/@srcset")
        loader.add_xpath('article_number', "//span[@slot='article']/text()")
        yield loader.load_item()
