from sys import argv
from requests import get
from bs4 import BeautifulSoup
from urllib import urlretrieve


script, tumblr_blog = argv

tumblr_url = 'http://' + tumblr_blog + '.tumblr.com'
tumblr_req = get(tumblr_url)
tumblr_html = tumblr_req.text

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
        continue

    image_url = link.get('src')

    if 'photoset' in link.parent.get('class')[0]:
        caption = link.find_next("div", "captions")
        username = caption.a.get_text()
        description = caption.blockquote.find_all('p')
        part_of_a_set = True
    else:
        caption = link.get('alt')
        username = caption.split(':')[0]
        description = caption.split(':')[1].strip()
        part_of_a_set = False

    image_urls.append(image_url)
    usernames.append(username)
    descriptions.append(description)
    photosets.append(part_of_a_set)

for indexA in xrange(len(image_urls) - 1, 0, -1): # counts down from the top so items can be removed correctly
    if '_1280' in image_urls[indexA]:
        continue
    imagefilenameA = image_urls[indexA].split('/')[-1]
    for indexB in xrange(0, len(image_urls) - 1, 1):
        imagefilenameB = image_urls[indexB].split('/')[-1]
        if (imagefilenameA.replace('_500', '_1280') == imagefilenameB) & (imagefilenameA != imagefilenameB):
            # delete lower pixel duplicates
            image_urls.pop(indexA)
            usernames.pop(indexA)
            descriptions.pop(indexA)
            photosets.pop(indexA)

for image_url in image_urls:
    print image_url
    # download pictures
    urlretrieve(image_url, download_folder + image_url.split('/')[-1])
