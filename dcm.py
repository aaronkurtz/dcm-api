# Copyright (c) 2012    Aaron Kurtz

from bs4 import BeautifulSoup
import urllib2
import re

INDEX_URL = "http://digitalcomicmuseum.com/index.php?dlid="
PREVIEW_URL = "http://digitalcomicmuseum.com/preview/index.php?did="

def category_strip(link):
  category = link['href'].rpartition('=')[2]
  return (category, link.string)

def read_index_page(soup):
  data = {}
  home = soup.find('a',text='Home')
  data['name'] = home.find_next_sibling('a', href=re.compile('dlid')).string
  categories = home.find_next_siblings('a', href=re.compile('cid'))
#TODO strip out urls with CIDs to save category data - list of tuple pairs (CID, Name)
  data['category'] = [category_strip(x) for x in categories]
  data['thumbnail'] = soup.find('img',src=re.compile('thumbnails'))['src']
  desc_header = soup.find(text='> Description')
  if desc_header:
    data['description'] = '\n'.join(desc_header.find_next('tr',class_='mainrow').stripped_strings)
  else:
    data['description'] = ''
  data['previewid'] = soup.find('a',{'href':re.compile("preview")})['href'].rpartition('=')[2] 
  return data

def read_preview_page(soup):
  data = {}
  pages = soup.find_all('img',{'alt':'no previous page'})[0].next_element.strip().split(' ') or False
  data['first page'] = pages[1]
  data['last page'] = pages[3]
  return data
  
def get_comic(idnum):
  data = {'id':idnum}
  index = BeautifulSoup(urllib2.urlopen(INDEX_URL+str(idnum)))
  data.update(read_index_page(index))
  preview = BeautifulSoup(urllib2.urlopen(PREVIEW_URL+str(data['previewid'])))
  try:
      data.update(read_preview_page(preview))
  except IndexError: #Broken page
      return None
  return data

def is_valid_comic(idnum):
  index = BeautifulSoup(urllib2.urlopen(INDEX_URL+str(idnum)))
  if index.find('img',{'src':'http://digitalcomicmuseum.com/skins/skin2/images/error.gif'}):
    return False
  else:
    return True

def grab_ids(pagesoup):
  idlist = pagesoup.find_all('a',{'href':re.compile('dlid')})
  checklist = [x['href'].rpartition('=')[2] for x in idlist]
  return checklist

def bot(url="http://digitalcomicmuseum.com/stats.php?ACT=latest&start=0&limit=100"):
  soup = BeautifulSoup(urllib2.urlopen(url))
  comic_ids = grab_ids(soup)
  if len(comic_ids) == 0:
      return [], None
  next_url = soup.find('img',{'alt':'Next'}).previous_element['href']
  return comic_ids, next_url

def return_comic_url(comic_id):
  return INDEX_URL+str(comic_id)

def return_page_url(preview_id, page_number):
  return PREVIEW_URL+str(preview_id)+"&page="+str(page_number)
