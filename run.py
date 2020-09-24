from scrapy import cmdline

cmdline.execute('scrapy crawl yahoo -o yahoo.csv'.split())