import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import KkybankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class KkybankSpider(scrapy.Spider):
	name = 'kybank'
	start_urls = ['https://www.kybank.com/topics/']

	def parse(self, response):
		post_links = response.xpath('//div[@style="padding-top:15px;"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//div[@class="prev-posts-link"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//meta[@property="article:published_time"]/@content').get().split('T')[0]
		title = ''.join(response.xpath('//h1//text()').getall())
		content = response.xpath('//div[@class="textwidget"]//text() |//div[@class="siteorigin-widget-tinymce textwidget"]//text() |//div[@class="rgt-cont-hld cms-content equalhei"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=KkybankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
