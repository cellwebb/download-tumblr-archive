from sys import argv
from requests import get
from bs4 import BeautifulSoup
from urllib import urlretrieve
from pprint import pprint

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

tumblr_url = 'http://' + tumblr_blog + '.tumblr.com'

NUMBER_OF_SCROLLS = 10
WAIT_BETWEEN_SCROLLS = 3
DOWNLOADING = True
DOWNLOAD_FOLDER = 'downloadedpics/'

image_urls = []
permalinks = []

print(chr(27) + "[2J") # clears terminal

driver = webdriver.Firefox()
driver.implicitly_wait(30)
driver.get(tumblr_url)


with open('blog_data.csv','wb') as csvfile:
    wr = UnicodeWriter(csvfile, quoting=csv.QUOTE_ALL)
    row = ['image_url', 'permalink', 'post_title', 'post_date', 'notes', 'username', 'caption']
    wr.writerow(row)

    driver.find_element("id","posts-wrapper").click()

    for scroll_counter in range(0,NUMBER_OF_SCROLLS):
        driver.execute_script("window.scrollByPages(1);")
        percent = (scroll_counter + 1)*100/NUMBER_OF_SCROLLS
        print "scrolling... (%s%%)" % (percent)
        #print "page source length:", len(driver.page_source)
        time.sleep(WAIT_BETWEEN_SCROLLS)

        tumblr_html = driver.page_source
        soup = BeautifulSoup(tumblr_html)

        for post in soup.find_all(class_ = "photo"):
            caption = post.next_sibling.find_next(class_ = 'captions').get_text().strip()

            # try:
            # caption = caption.blockquote.get_text()
            # except AttributeError:
            # caption = caption.get_text().strip()

            permalink = post.next_sibling.find_next(class_ = 'details').a.get('href')

            details = post.next_sibling.find_next(class_ = 'details')
            title = permalink.split('/')[-1]
            try:
                notes = details.find_all('a')[1].get_text()
                #print notes
            except AttributeError:
                print "AttributeError"
                pprint(details.find_all('a'))

            post_date = ''
            username = ''
            # if post_info.find(class_ = 'captions').p.a.get('href'):

            #print post.div.get('class')
            if post.div.get('class') == ['photo-hover']:
                image_url = post.img.get('src')
                for low_res in ['_250', '_400', '_500', '_540']:
                    image_url = image_url.replace(low_res ,'_1280')

                if not '_1280' in image_url:
                    print image_url

                if image_url in image_urls:
                    #print "caught!"
                    continue

                image_urls.append(image_url)
                row = [image_url, permalink, title, post_date, notes, username, caption]
                # print row
                try:
                    wr.writerow(row)
                except UnicodeError:
                    print "Unicode Error: \n", row

            elif post.div.get('class') == ['photoset-grid']:
                # photosets need special rules
                photoset_images = post.find_all('img')

                for photo in photoset_images:
                    image_url = photo.get('src')
                    for low_res in ['_250', '_400', '_500', '_540']:
                        image_url = image_url.replace(low_res ,'_1280')

                    if not '_1280' in image_url:
                        print image_url

                    if image_url in image_urls:
                        #print "caught!"
                        continue

                    image_urls.append(image_url)

                    row = [image_url, permalink, title, post_date, notes, username, caption]

                    try:
                        wr.writerow(row)
                    except UnicodeError:
                        print "Unicode Error: \n", row
            else:
                print post.div.get('class')

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
