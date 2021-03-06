# -*- coding: utf-8 -*-

# Scrapy settings for oyez project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'oyez'

SPIDER_MODULES = ['scotus.spiders']
NEWSPIDER_MODULE = 'scotus.spiders'
CONCURRENT_REQUESTS = 5
DOWNLOAD_DELAY = .75 


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36'

# other settings

SCDB_ISSUES_FILE = 'data/scdb/SCDB_2015_01_caseCentered_LegalProvision.csv'
SCDB_CASES_FILE =  'data/scdb/SCDB_2015_01_caseCentered_Citation.csv'
SCDB_VOTES_FILE = 'data/scdb/SCDB_2015_01_justiceCentered_Citation.csv'
SCDB_TEST_FILE = 'data/scdb/SCDB_TEST.csv'

JUSTICES_FILE = 'data/oyez/justices.json'
  
DEFAULT_DB = 'sqlite:///scotus.db'
TEST_DB = 'sqlite:///test_scotus.db'