from PlaywrightDriver import PlaywrightDriver
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time as t
import pandas as pd
from GoogleFormsSubmitter import GoogleFormsSubmitter

class MondaybroadcastFetcher:
    def __init__(self, url, cookies_file='D:\Automate the Inputsheet\data\cookies\kits_cookies.json'):
        self.url = url
        self.cookies_file = cookies_file
        self.driver = PlaywrightDriver(cookies_file=self.cookies_file)
        self.context = self.driver.initialize_driver()
        self.page = self.context.new_page()

    def goToBroadCastsPage(self):
        # Reuse the existing page
        self.page.goto(self.url)
        t.sleep(5)
        return self.page

    def findLastMondayDate(self):
        current_date = datetime.now()
        last_monday = current_date - timedelta(days=current_date.weekday())  # Weekday with no value set to it means it's Monday.
        return last_monday.strftime('%Y-%m-%d')
    
    def identifyLastMondaySequence(self):
        self.goToBroadCastsPage()
        last_monday_date = self.findLastMondayDate()
        page_content = self.page.content()
        soup = BeautifulSoup(page_content, "html.parser")

        # Get all dates in the page
        time_tags = soup.find_all("time")
        for time_tag in time_tags:
            datetime_attr = time_tag.get("datetime")
            if datetime_attr and last_monday_date in datetime_attr:
                # This is the date match, Get the ID 
                parent_li = time_tag.find_parent("li")
                if parent_li:
                    sequence_link = parent_li.find("a", class_="hover:no-underline")
                    if sequence_link:
                        sequence_id = sequence_link["href"].split("/")[2]  # Extract sequence ID
                        return sequence_id
            else:
                print("Could not match the dates. Fuckin GPT!!")
    

    def goToSequence(self, id):
        sequence_id = id
        if sequence_id:
            self.page.goto(f"https://app.kit.com/publications/{sequence_id}/reports/overview")
            t.sleep(50)
            print("Second and half of many.. Not bad, no pressure also, time is of the essennce!")
        else:
            print("Sequence ID not found. No pressure, but check your dates!")

    def getSequenceData(self):
        page_content = self.page.content()
        soup = BeautifulSoup(page_content, "html.parser")
        report_data = {"Total recipients": None, "Open rate": None, "Click rate": None}
        
        for h4 in soup.find_all("h4"):
            h4_text = h4.get_text(strip=True)
            if h4_text in report_data:
                parent = h4.parent
                found_value = None
                # Explicitly check within the immediate <div> under parent
                number_div = parent.find("div", class_="font-mono text-3xl text-yellow-600")
                if number_div:
                    text = number_div.get_text(strip=True)
                    if text.replace(",", "").replace("%", "").isdigit() or "%" in text:
                        found_value = text
                
                if found_value:
                    report_data[h4_text] = found_value

        print("Report Data:")
        for key, value in report_data.items():
            print(f"{key}: {value}")
        return report_data
    
    def goToSequence(self, sequence_id = None):
        sequence_id = self.identifyLastMondaySequence()
        if sequence_id:
            self.page.goto(f"https://app.kit.com/publications/{sequence_id}/reports/overview")
            t.sleep(5)
            print("Second and half of many.. Not bad, no pressure also, time is of the essennce!")
            self.getSequenceData()
        else:
            print("Sequence ID not found. No pressure, but check your dates!")

    def submitBroadCastData(self):
        # Load form and entry mappings manually like form_fields_1
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfXbTrBgq4l_UUcQyduVANjwb1qg6ZZbE7tqMmewezghiBHcA/formResponse"
        form_fields = {
            'Total recipients': 'entry.1805050348',
            'Open rate': 'entry.1597220645',
            'Click rate': 'entry.2132538116'
        }

        # Extract report data
        report_data = self.getSequenceData()
        print("Report Data Before Submission:", report_data)

        # Map the data explicitly using keys
        mapped_data = {
            'Total recipients': report_data['Total recipients'],
            'Open rate': report_data['Open rate'],
            'Click rate': report_data['Click rate']
        }

        print("Mapped Data to Submit:", mapped_data)

        # Submit the data
        form_submitter = GoogleFormsSubmitter(form_url, form_fields)
        form_submitter.submit_data(mapped_data)
        print("Broadcast data submitted successfully.")



    def close(self):
        self.context.close()
        self.driver.close(self.context)

if __name__ == "__main__":
    fetcher = MondaybroadcastFetcher("https://app.kit.com/campaigns")
    try:
        fetcher.goToSequence()
        fetcher.submitBroadCastData()
    finally:
        fetcher.close()
