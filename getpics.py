from sys import argv
from requests import get
from bs4 import BeautifulSoup
from urllib import urlretrieve

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import sys

import unittest, time, re



script, tumblr_blog = argv

tumblr_url = 'http://' + tumblr_blog + '.tumblr.com'


driver = webdriver.Firefox()
driver.implicitly_wait(30)
verificationErrors = []
accept_next_alert = True
#time.sleep(10)
driver.get(tumblr_url)
time.sleep(10)
driver.find_element("id","posts-wrapper").click()
print "clicking..."
time.sleep(10)
scrolls = 2
for i in range(0,scrolls):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    print "scrolling... (%r\%)" % ((i+1)/scrolls)
    time.sleep(4)
tumblr_html = driver.page_source
#print tumblr_html
driver.quit()


download_folder = 'downloadedpics/'

soup = BeautifulSoup(tumblr_html)

image_urls = []
# usernames = []
# descriptions = []
# photosets = []

#extract all image URLs with special rules for photosets
for link in soup.find_all('img'):
    if 'px.srvcs' in link.get('src'):
        # skip any urls from 'pixel services'
        continue

    image_url = link.get('src')
    print image_url
    print type(image_url)

    # if 'photoset' in link.parent:
    #     caption = link.find_next("div", "captions")
    #     username = caption.a.get_text()
    #     description = caption.blockquote.find_all('p')
    #     part_of_a_set = True
    # else:
    #     caption = link.get('alt')
    #     if type(caption) == "NoneType":
    #         caption = link.get('title')
    #     username = caption.split(':')[0]
    #     description = caption.split(':')[1].strip()
    #     part_of_a_set = False

    image_urls.append(image_url)
    # usernames.append(username)
    # descriptions.append(description)
    # photosets.append(part_of_a_set)

for indexA in xrange(len(image_urls) - 1, 0, -1): # counts down from the top so items can be removed correctly
    if '_1280' in image_urls[indexA]:
        continue
    imagefilenameA = image_urls[indexA].split('/')[-1]
    # for indexB in xrange(0, len(image_urls) - 1, 1):
    #     imagefilenameB = image_urls[indexB].split('/')[-1]
    #     if (imagefilenameA.replace('_500', '_1280') == imagefilenameB) & (imagefilenameA != imagefilenameB):
    #         # delete lower pixel duplicates
    #         image_urls.pop(indexA)
    #         print "POP!"
            # usernames.pop(indexA)
            # descriptions.pop(indexA)
            # photosets.pop(indexA)

for image_url in image_urls:
    print image_url
    # download pictures
    urlretrieve(image_url, download_folder + image_url.split('/')[-1])
