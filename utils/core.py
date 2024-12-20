import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time as t
from bs4 import BeautifulSoup
import pandas as pd
from utils.CookiesCleaner import CookiesCleaner
import json
from dotenv import load_dotenv

class InfoParser:
    def __init__(self, context):
        self.context = context

    def scrap_info(self, link):
        page = self.context.new_page()
        page.goto(link, timeout=1200000000)
        t.sleep(8) 
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        page.close()
        return self._parse_info(soup)


class PageInfoParser(InfoParser):
    def _parse_info(self, soup):
        all_p_tags = soup.find_all('p')
        for i, tag in enumerate(all_p_tags):
            if tag.get_text(strip=True) == "Post impressions":
                if i > 0:
                    previous_p_tag = all_p_tags[i - 1]
                    return FollowersTracker.clean_text(previous_p_tag.get_text(strip=True))
        
        return 'Not Found'






class FollowersTracker:
    def __init__(self, context, pages_file,):
        self.context = context
        self.pages = self.read_excel(pages_file)

    def login(self, username, password):
        page = self.context.new_page()
        page.goto("https://www.linkedin.com/login", timeout=60000)
        page.fill('input[name="session_key"]', username)
        page.fill('input[name="session_password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        new_cookies = self.context.cookies()
        cleaner = CookiesCleaner()
        cleaned_cookies = cleaner.clean_cookies(new_cookies)
        with open('cookies.json', 'w') as file:
            json.dump(cleaned_cookies, file)

        page.close()
        print("Login successful, cookies saved.")

    def read_excel(self, file_path):
        return pd.read_excel(file_path)

    def get_links(self):
        page_links = self.pages['Link'].tolist()
        
        return page_links

    def scrap_info(self):
        page_parser = PageInfoParser(self.context)
        page_links = self.get_links()

        followers_data = []
        for link in page_links:
            info = self._scrap_with_retry(page_parser, link)
            followers_data.append(info)
            print(f"Page info: {info}")
            print("Impressions Data:", followers_data)
        
        # Move the return statement outside the loop
        return followers_data


    def _scrap_with_retry(self, parser, *args,retry = True):
        load_dotenv(dotenv_path='D:\Automate the Inputsheet\enviromental_variables.env')
        info = parser.scrap_info(*args)
        if info == 'Not Found' and retry:
            print("Info not found, attempting login...")
            self.login(username=os.getenv('linkedin_username'), password=os.getenv('linkedin_password'))
            info = parser.scrap_info(*args)
        return info

    @staticmethod
    def clean_text(text):
        if text:
            text = text.replace(",", "").split(' ')[0]
            if text.isdigit():
                return int(text)
        return 'Not Found'