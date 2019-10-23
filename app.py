import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from liverpool.spiders.spider import LiverpoolSpider

if __name__ == '__main__':
	process = CrawlerProcess(get_project_settings())

	process.crawl(LiverpoolSpider)
	process.start()