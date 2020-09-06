import requests
from bs4 import BeautifulSoup
from difflib import get_close_matches
from selenium import webdriver
import pandas as pd

class CraigSearch:
    
    def __init__(self, craigslist_landing_url = None):

        self.craigslist_site = craigslist_landing_url
        self.search_terms = None
        self.category_selection = None 
        self.category_dict = None
        self.categories = None

    def start(self):
        
        response = requests.get(self.craigslist_site)
        soup = BeautifulSoup(response.text, 'html.parser')

        page_elements = [i.find('a') for i in soup.findAll('h4',{'class':'ban'})]

        categories = [i.text for i in soup.findAll('h4', {'class':'ban'})]
        links = [i.get('href') for i in page_elements]
        category_dict = dict(zip(categories,links))
        self.category_dict = category_dict
        self.categories = list(self.category_dict.keys())
        
        print(self.categories)
    
    def set_params(self, category, search_terms):

        self.category_selection = category
        self.search_terms = search_terms

    def get_results(self):
        
        driver = webdriver.Chrome()
        entry_url = self.craigslist_site + self.category_dict[self.category_selection]
        if entry_url[:8] == 'https://':
            entry_url = 'https://' + entry_url[8:].replace('//','/')
        else:
            entry_url = 'https://' + entry_url.replace('//','/')
        driver.get(entry_url)
        driver.find_element_by_xpath("""//*[@id="query"]""").send_keys(self.search_terms)
        driver.find_element_by_xpath("""//*[@id="searchform"]/div[1]/button""").click()
        current_page_url = driver.current_url
        response = requests.get(entry_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
       
        max_page = int(soup.find('span', {'class':'totalcount'}).text)  
        current_page_to = 0
        
        dates = []
        titles = []
        prices = []
        neighborhoods = []
        links = []
        posts = []
        longitudes = []
        latitudes = []
        attrs = []
        while current_page_to < max_page:
            
            current_url = driver.current_url
            
            response = requests.get(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            boxes = soup.findAll('li', {'class':'result-row'})
        
            result_info = [i.find('p') for  i in boxes]
            page_links = [i.find('a',{'class':'result-title hdrlnk'}).get('href') for i in result_info] 
            
            for i in boxes:
                try:
                    neighborhoods.append(i.find('span', {'class':'result-hood'}).text)
                except:
                    neighborhoods.append('Not Listed')
            for i in result_info:
                try:
                    dates.append(i.find('time', {'class':'result-date'}).get('datetime'))
                    titles.append(i.find('a',{'class':'result-title hdrlnk'}).text)
                    prices.append(i.find('span', {'class':'result-price'}).text.replace('$',''))
                    links.append(i.find('a',{'class':'result-title hdrlnk'}).get('href'))
                except:
                    titles.append('Not Found')
                    dates.append('Not Found')
                    prices.append('Not Found')
                    links.append('Not Found')
            
            for link in page_links:
                driver.get(link)
                current_url = driver.current_url
                response = requests.get(link)
                soup = BeautifulSoup(response.text, 'html.parser')
                post = soup.find('section', {'id':'postingbody'}).text
                posts.append(post)
                #attr = soup.get('p',{'class':'attrgroup'}).text
                try:
                    lat = soup.find('div', {'id':'map'}).get('data-latitude')
                    lon = soup.find('div',{'id':'map'}).get('data-longitude')
                    latitudes.append(lat)
                    longitudes.append(lon)
                except:
                    #attrs.append(attr)
                    latitudes.append('')
                    longitudes.append('')
                    # attrs.append('')
            
            page_links = []
            driver.get(current_page_url)   

            # links = [i.find('a',{'class':'result-title hdrlnk'}).get('href') for i in result_info]
            try:
                driver.find_element_by_xpath("""//*[@id="searchform"]/div[5]/div[3]/span[2]/a[3]""").click()
                current_page_to = int(soup.find('span', {'class':'rangeTo'}).text)
            except:
                break

        
        atr_list = ['Date', 'Title', 'Price', 'Neighborhood', 'Link', "Post",'Latitude', 'Longitude', ]
    
        table = pd.DataFrame(list(zip(dates, titles, prices, neighborhoods, links, posts, latitudes, longitudes,)), columns=atr_list)
        driver.close()
        return table 


        
