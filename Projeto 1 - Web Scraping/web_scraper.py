# imports
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import requests 
import schedule
import time

# get filepath

path = os.path.dirname(os.path.abspath(__file__))
path = path + '/data.csv' # this will put the data on the same folder of this file

# Website urls

base_url = "http://books.toscrape.com/index.html"

def getAndParseURL(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    return soup

def getBooksURLs(url):
    soup = getAndParseURL(url)
    # remove index.html before returning the results
    page_products_urls = ["/".join(url.split("/")[:-1]) + "/"  + x.div.a.get('href') for x in soup.findAll("article", class_ = "product_pod")]
    return page_products_urls

def getCategoriesURLs(url):
    soup = getAndParseURL(url)
    categories_urls = ["/".join(url.split("/")[:-1]) + "/" + x.get('href') for x in soup.findAll('a', href = re.compile('catalogue/category/books'))]
    categories_urls = categories_urls[1:]
    return categories_urls

def getPagesURLs(url):
    pages_urls = [url]
    soup = getAndParseURL (pages_urls[0])
    while ((len(soup.findAll("a", href = re.compile("page"))) == 2) or (len(pages_urls) == 1)): # check if there is a next and a previous page button
        # get the new complete url by adding the fetched url to the base url(and removing the index.html part of the base url)
        new_url = "/".join(pages_urls[-1].split("/")[:-1]) + "/" + soup.findAll("a", href = re.compile("page"))[-1].get('href')
        # add the url to the list
        pages_urls.append(new_url)
        # jump to the next page
        soup = getAndParseURL(new_url)
    return pages_urls



def job():

    books_urls = [getBooksURLs(x) for x in getPagesURLs(base_url)] # 50 lists of 20 itens
    books_urls = [book for page in books_urls for book in page] # flatten the list of lists

    # create list to store the collected data
    names = []
    prices = []
    books_in_stock = []
    img_urls = []
    categories = []
    ratings = []

    for book in books_urls:
        soup = getAndParseURL(book)
        # names=
        names.append(soup.find("div", class_ = re.compile("product_main")).h1.text)
        # product price
        prices.append(soup.find("p", class_ = "price_color").text[2:]) # get rid of the pound sign
        # number of available products
        books_in_stock.append(re.sub("[^0-9]", "", soup.find("p", class_ = "instock availability").text)) # get rid of non numerical characters
        # image url
        img_urls.append(book.replace("index.html", "") + soup.find("img").get("src"))
        # product category
        categories.append(soup.find("a", href = re.compile("../category/books/")).get("href").split("/")[3])
        # ratings
        ratings.append(soup.find("p", class_ = re.compile("star-rating")).get("class")[1])



    df = pd.DataFrame({'name' : names, 'price' : prices, 'books_in_stock' : books_in_stock, 'price' : prices, 'category' : categories, 'rating' : ratings, 'url_img' : img_urls})
    df.to_csv(path)

    print("I'm working...")

schedule.every().day.at("15:20").do(job) # set the time of the day to run the script

while True:
    schedule.run_pending()
    time.sleep(1)
