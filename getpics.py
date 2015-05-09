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
import csv

import time

script, tumblr_blog = argv

tumblr_url = 'http://' + tumblr_blog + '.tumblr.com'


print(chr(27) + "[2J") # clear terminal

scrolling = False
downloading = False

driver = webdriver.Firefox()
driver.implicitly_wait(30)
driver.get(tumblr_url)
if scrolling == True:
    delay = 3
    for i in range(delay):
        print i
        time.sleep(1)
    driver.find_element("id","posts-wrapper").click()
    print "clicking..."
    delay = 3
    for i in range(delay):
        print i
        time.sleep(1)
    scrolls = 2
    for i in range(0,scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        percent = (i + 1)*100/scrolls
        print "scrolling... (%s)" % (percent)
        time.sleep(2)
tumblr_html = driver.page_source
driver.quit()

download_folder = 'downloadedpics/'

soup = BeautifulSoup(tumblr_html)

image_urls = []
usernames = []
descriptions = []
photosets = []

#extract all image URLs with special rules for photosets
for link in soup.find_all('img'):
    if 'px.srvcs' in link.get('src'):
        # skip any urls from 'pixel services'
        print "px.srvcs avoided"
        continue
    if '.gif' in link.get('src'):
        # skip over the ajax loader
        continue

    image_url = link.get('src')

    caption = ''
    username = ''
    description = ''
    part_of_a_set = False

    try:
        if 'photoset-row' in link.parent.parent.get('class'):
            part_of_a_set = True
        else:
            if 'normal-width' in link.parent.get('class'):
                # under the assumption that normal-width images
                # always come with larger-width versions, we'll
                # skip the normal-width ones
                continue
        caption = link.find_next('div', 'captions')
        username = caption.p.a.get_text()
        description = caption.blockquote.get_text()
    except TypeError:
        if 'instagram' in link.parent.parent.parent.get('id'):
            if link.has_attr('title'):
                caption = link.get('title')
            else:
                print "instagram, no title", link
        try:
            if '@' in caption:
                username = caption.split('@')[1]
                description = caption.split('@')[0]
            else:
                # print "no :, no @", link
                username = "tumblr_blog"
                description = caption
        except IndexError:
            print "IndexError"
            # print caption
            # print link
            # print link.parent
            # sys.exit()

    image_urls.append(image_url)
    usernames.append(username)
    descriptions.append(description)
    photosets.append(part_of_a_set)

for image_url in image_urls:
    print image_url

for description in descriptions:
    print description

if downloading:
    print "Now downloading %r images." % (len(image_urls))
    for image_url in image_urls:
        urlretrieve(image_url, download_folder + image_url.split('/')[-1])
