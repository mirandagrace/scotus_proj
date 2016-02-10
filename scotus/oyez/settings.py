# -*- coding: utf-8 -*-

# Scrapy settings for oyez project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'oyez'

SPIDER_MODULES = ['oyez.spiders']
NEWSPIDER_MODULE = 'oyez.spiders'
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 1

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36'