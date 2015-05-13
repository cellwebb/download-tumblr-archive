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
import sys, os, csv, time

from UnicodeWriter import UnicodeWriter
from id_generator import id_generator

start_time = time.time()

script, tumblr_blog = argv

tumblr_url = 'http://' + tumblr_blog + '.tumblr.com/archive'

NUMBER_OF_SCROLLS = 20
WAIT_BETWEEN_SCROLLS = 3
DOWNLOADING = True
DOWNLOAD_FOLDER = 'downloadedpics/'

image_urls = []
permalinks = []

print(chr(27) + "[2J") # clears terminal

driver = webdriver.Firefox()
driver.implicitly_wait(30)
driver.get(tumblr_url)


with open('archive_data.csv','wb') as csvfile:
    wr = UnicodeWriter(csvfile, quoting=csv.QUOTE_ALL)
    row = ['image_url', 'permalink', 'post_title', 'post_date', 'notes']
    wr.writerow(row)

    driver.find_element("id","body").click()

    for scroll_counter in range(0,NUMBER_OF_SCROLLS):
        driver.execute_script("window.scrollByPages(1);")
        percent = (scroll_counter + 1)*100/NUMBER_OF_SCROLLS
        print "scrolling... (%s%%)" % (percent)
        #print "page source length:", len(driver.page_source)
        time.sleep(WAIT_BETWEEN_SCROLLS)

        tumblr_html = driver.page_source
        #driver.quit()

        soup = BeautifulSoup(tumblr_html)

        #extract all image URLs with special rules for photosets
        for link in soup.find_all(class_ = "post_content"):

            image_url = link.div.div.get('data-imageurl')
            image_url = image_url.replace('_250', '_1280')

            if image_url in image_urls:
                print "caught!"
                continue

            image_urls.append(image_url)
            permalink = link.next_sibling.a.get('href')
            title = permalink.split('/')[-1]
            post_date = link.next_sibling.find(class_ = 'post_date').get_text()
            notes = link.next_sibling.find(class_ = 'post_notes').get('data-notes')

            row = [image_url, permalink, title, post_date, notes]
            # print row
            try:
                wr.writerow(row)
            except UnicodeError:
                print "Unicode Error: \n", row

driver.quit()

if DOWNLOADING:
    print "Now downloading %r images." % (len(image_urls))
    for image_url in image_urls:
        filename = image_url.split('/')[-1]
        if not os.path.exists(DOWNLOAD_FOLDER + filename):
            urlretrieve(image_url, DOWNLOAD_FOLDER + filename)
        image_index = image_urls.index(image_url)
        if image_index % 10 == 0:
            print "images downloaded: %d (%.2f%% complete)" % (image_index, image_index*100/len(image_urls))

print "Elapsed time: %.2f seconds" % (time.time() - start_time)
