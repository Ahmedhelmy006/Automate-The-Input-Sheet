import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.PlaywrightDriver import PlaywrightDriver
from utils.core import FollowersTracker
from utils.GoogleFormsSubmitter import GoogleFormsSubmitter
from dotenv import load_dotenv

def run_scraper():
    driver = PlaywrightDriver(cookies_file='D:\Automate the Inputsheet\data\cookies\lkd_account.json')
    context = driver.initialize_driver()

    # Scrape followers data
    tracker = FollowersTracker(
        context,
        r'D:\Automate the Inputsheet\data\Page Links\Pages.xlsx',
    )
    
    followers_data = tracker.scrap_info()
    print("Followers Data:", followers_data)

    load_dotenv(dotenv_path="D:\Automate the Inputsheet\enviromental_variables.env")
    form_url=os.getenv('linkedin_weekly_stats_form')
    
    form_fields_1 = {
        'Business Infographics': 'entry.713216161',
        'Nicolas Boucher Online': 'entry.1839383127',
        'AI Finance Club': 'entry.1810533523'
    }

    mapped_data_1 = {
        'Business Infographics': followers_data[0],
        'Nicolas Boucher Online': followers_data[1],
        'AI Finance Club': followers_data[2], 
    }

    form_submitter = GoogleFormsSubmitter(form_url, form_fields_1)
    form_submitter.submit_data(mapped_data_1)

    driver.close(context)

while True:
    run_scraper()