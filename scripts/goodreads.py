import argparse
from collections import Counter
from datetime import datetime
import json
import os
import regex as re
import time
import bs4
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException, ElementNotVisibleException, StaleElementReferenceException
from selenium.webdriver.support.ui import Select
from urllib.request import urlopen
from urllib.error import HTTPError
from selenium.webdriver.common.by import By
import pandas as pd
import geckodriver_autoinstaller
from webdriver_manager.chrome import ChromeDriverManager


def get_rating_from_text(rating_text):
    rating_dict = {'did not like it': '1',
                   'it was ok': '2',
                   'liked it': '3',
                   'really liked it': '4',
                   'it was amazing': '5'}

    return rating_dict[rating_text]

def get_title(node):
    if len(node.find_all('td', {'class': 'field title'})) > 0:
        return (node.find_all('td', {'class': 'field title'})[0].contents[1].contents[1].attrs['title'])
    return ''

def get_link(node):
    if len(node.find_all('td', {'class': 'field title'})) > 0:
        href = node.find_all('td', {'class': 'field title'})[0].contents[1].contents[1].attrs['href']
        return (f'https://www.goodreads.com{href}')
    return ''

def get_author(node):
    if len(node.find_all('td', {'class': 'field author'})) > 0:
        return (node.find_all('td', {'class': 'field author'})[0].contents[1].contents[1].contents[0])
    return ''

def get_author_link(node):
    if len(node.find_all('td', {'class': 'field author'})) > 0:
        href = node.find_all('td', {'class': 'field author'})[0].contents[1].contents[1].attrs['href']
        return (f'https://www.goodreads.com{href}')
    return ''

def get_img_src(node):
    if len(node.find_all('td', {'class': 'field cover'})) > 0:
        return (node.find_all('td', {'class': 'field cover'})[0].contents[1].contents[1].contents[1].contents[0].attrs['src'])
    return ''

def get_rating(node):
    if len(node.find_all('td', {'class': 'field rating'})) > 0:
        td = node.find_all('td', {'class':'field rating'})[0]
        span = td.find_all('span', {'class':'staticStars notranslate'})[0]
        rating_text = span.get('title')
        rating = get_rating_from_text(rating_text)
        return rating
    return ''

def get_book_info(driver, userID, previous=True):
    books = []
    if previous:
        url = f'https://www.goodreads.com/review/list/{userID}?shelf=read'
    else:
        url = f'https://www.goodreads.com/review/list/{userID}?shelf=currently-reading'
    
    driver.get(url)

    source = driver.page_source
    time.sleep(4)
    books = []

    source = driver.page_source
    soup = bs4.BeautifulSoup(source, 'lxml')
    nodes = soup.find_all('tr', {'class': 'bookalike review'})
    for node in nodes:
        b = {
            'title': get_title(node),
            'link': get_link(node),
            'author': get_author(node),
            'author_link': get_author_link(node),
            'img_src': get_img_src(node)
        }
        if previous:
            b['rating'] = get_rating(node)
            b['review_link'] = url
        books.append(b)
    return books

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user_id', type=str)
    parser.add_argument('--out_markdown', type=str)

    args = parser.parse_args()

    if not args.user_id:
        parser.error("\n\nPlease add a user id with --user_id flag")
    if not args.out_markdown:
        parser.error("\n\nPlease add an output file path with --out_markdown flag")
    
    userID = args.user_id
    outPath = args.out_markdown

    driver = webdriver.Chrome(ChromeDriverManager().install())
    
    currently_reading = get_book_info(driver, userID, previous=False)

    out_file_text = "# Currently Reading\n\n"
    for b in currently_reading:
        out_file_text += "{{<booktile" + f'''
        title="{b['title']}"
        link="{b['link']}"
        author="{b['author']}"
        author_link="{b['author_link']}"
        img_src="{b['img_src']}"
        ''' + ">}}\n"

    previously_read = get_book_info(driver, userID)
    out_file_text += "# Previously Read\n"
    for b in previously_read:
        out_file_text += "{{<oldbooktile" + f'''
        title="{b['title']}"
        link="{b['link']}"
        author="{b['author']}"
        author_link="{b['author_link']}"
        img_src="{b['img_src']}"
        rating="{b['rating']}"
        review_link="{b['review_link']}"
        ''' + ">}}\n"
    

    outFile = myFile = open(outPath, 'w') # or 'a' to add text instead of truncate
    myFile.write(out_file_text)
    myFile.close()
    

if __name__ == '__main__':
    main()