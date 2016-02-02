__author__ = 'natelawrence'

import urllib
from bs4 import BeautifulSoup
import csv


filename = 'SantaClaraSandwiches.csv'
searchterm = 'Sandwiches'
location = 'Santa+Clara+CA'

searchurl = u'http://www.yelp.com/search?find_desc={}&find_loc={}'.format(searchterm,location)

hrefList = []
nBiz = 500

start = 0
while len(hrefList)<nBiz:
    html = urllib.urlopen(searchurl+'&start={}'.format(start)).read()
    soup = BeautifulSoup(html)
    searchResults = soup.find_all('li',class_='regular-search-result')
    for result in searchResults:
        hrefList.append(result.find('a').get('href'))
    start = start+10
    print(['href',len(hrefList)])


for hh in range(158,len(hrefList)):
    href = hrefList[hh]
    if href.find(u'?')>0:
        href = href[0:href.find(u'?')]
    #review_text = []
    review_stars = []
    review_username = []
    review_id = []
    id = href[5:]
    url = 'http://www.yelp.com'+href

    start = 0
    while True:
        html = urllib.urlopen(url+'?start={}'.format(start)).read()
        soup = BeautifulSoup(html)

        reviews = soup.find_all("div", class_="review review--with-sidebar")
        if len(reviews)<2:
            break
        else:
            reviews.pop(0) #first item in list is not a review
            for item in reviews:
                #text = item.find("div",class_='review-content').find('p').get_text()
                stars = float(item.find("div",class_='review-content').find('meta').get('content'))
                username = item.get('data-signup-object')[8:]
                #review_text.append(text)
                review_stars.append(stars)
                review_username.append(username)
                review_id.append(id)
            start = start+20
            print [hh, id, len(review_stars)]

    with open(filename, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ')
        for ii in range(0,len(review_stars)):
            writer.writerow([review_id[ii].encode('utf-8'),review_username[ii].encode('utf-8'),review_stars[ii]])

