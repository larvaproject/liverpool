import scrapy
from scrapy.http import Request
import csv
import time
import calendar
from datetime import datetime, date
from ..items import LiverpoolItem

from scrapy.linkextractors import LinkExtractor

import requests
from urllib.request import urlopen
import urllib.request
import xml.etree.ElementTree as ET

def getFecha():
	#Traemos la fecha
	x = datetime.now()

	dia = str(x.strftime("%d"))
	mes = str(x.strftime("%m"))
	anio = str(x.year)

	return dia + '_' + mes + '_' + anio

def getName(count):
	return 'sitemap.' + str(count) + '_'+ getFecha()

def loadSitemap(sitemapList):
	count = 0
	listNames = []
	
	#Eliminamos los dos ulitmos
	sitemapList.pop()
	sitemapList.pop()

	print(sitemapList)
	for s in sitemapList :
		resp = requests.get(s)
		name = getName(count) + ".xml"
		with open(name, 'wb') as f:
			f.write(resp.content)
		listNames.append(name)
		count += 1
	return listNames

def loadRRS():
	url = 'https://www.liverpool.com.mx/Sitemap/index.xml'
	
	resp = requests.get(url)
	date = "liverpool_padre_" + getFecha() + '.xml'

	with open(date, 'wb') as f:
		f.write(resp.content)

	return date	

def parseXML(xmlFile):
	#Creamos el arbol
	tree = ET.parse(xmlFile)
	#Obtenemos la raiz
	root = tree.getroot()

	#Lista de almacenamiento
	listaP = []

	#Almacenamos aqui los items
	for movie in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
			link = movie.text 
			#print(link)
			listaP.append(link)
	return listaP	

def downloadUrl(listNames):
	listUrl = []
	for li in listNames:
		tree = ET.parse(li)
		root = tree.getroot()
		for r in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
			link = r.text
			listUrl.append(link)
		#Imprimimos la longitud de los items
	return listUrl	

def main():
	#Cargamos la URL del XML
	date = loadRRS()

	#Descargamos cada uno de los URLS
	xmlLinio = parseXML(date)

	#Descargamos cada link
	listNames = loadSitemap(xmlLinio)

	print(len(listNames))

	#Leemos todos los xml y los guardamos en una lista y leer todos los links
	return downloadUrl(listNames)
	

class LiverpoolSpider(scrapy.Spider):
	name = 'liverpool'
	allowed_domains = ["www.liverpool.com.mx"]

	def start_requests(self):
		urls = main()
		for i in urls:
			yield scrapy.Request(url=i, callback=self.parse_dir_contents, dont_filter = True, meta={'url':i})

	def parse_dir_contents(self, response):

		items = LiverpoolItem()

		url = response.meta.get('url')

		#Informacion del producto
		items['codigo'] = response.xpath('//*[@class="m-product__information--code"]/span/text()').extract()
		items ['nombre'] = response.xpath('//*[@class="a-product__information--title"]/text()').extract()
		items ['original'] = response.xpath('//*[@class="a-product__paragraphRegularPrice m-0 d-inline"]/text()[2]').extract()
		items ['descuento'] = response.xpath('//p[@class="a-product__paragraphDiscountPrice m-0 d-inline "]/text()[2]').extract()
		
		items ['categoria'] = response.xpath('//ul[@class="m-breadcrumb-list"]/li[2]/a/text()').extract()
		items ['marca'] = response.xpath('//*[@id="o-product__productSpecsDetails"]/div[2]/div/div/div/p[1]/span/text()').extract()
		items ['vendedor'] = response.xpath('//p[@class="a-productInfo_selledBy"]/a/text()').extract()
		
		items ['descripcion'] = response.xpath('//div[@class="tabs-content"]/div/text()').extract()
		items ['url'] = url
		items ['fecha'] = getFecha()
		
		yield items