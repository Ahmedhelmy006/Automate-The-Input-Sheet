import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.PlaywrightDriver import PlaywrightDriver
from bs4 import BeautifulSoup
import time as t
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, Dimension, Metric, Filter, FilterExpression

class WelcomeSequence:
    def __init__(self, cookies='D:\Automate the Inputsheet\data\cookies\kits_cookies.json', id=1904146):
        self.cookies = cookies
        self.driver = PlaywrightDriver(cookies_file=self.cookies)
        self.context = self.driver.initialize_driver()
        self.page = self.context.new_page()
        self.id = id
        load_dotenv(dotenv_path="D:\Automate the Inputsheet\enviromental_variables.env")
        self.client = BetaAnalyticsDataClient.from_service_account_file(os.getenv('json_key_path'))
        self.property_id = os.getenv('property_id')
        self.target_campaign = os.getenv('target_campaign')

    def navigateWelcomeSequence(self):
        link = f"https://app.kit.com/sequences/{self.id}/reports"
        self.page.goto(link)
        t.sleep(5)
        return self.page

    def obtainEmailsData(self):
        page = self.navigateWelcomeSequence()
        page_content = page.content()
        soup = BeautifulSoup(page_content, 'html.parser')
        emails_list = soup.find('ul', id='email_stats').find_all('li')
        emails = [e for e in emails_list if e.get('id')]
        return emails

    def extractEmailsData(self):
        emails = self.obtainEmailsData()
        emails_data = []
        for email in emails:
            title_tag = email.find('h4')
            if not title_tag:
                continue
            email_title = title_tag.get_text(strip=True)
            stats = email.find_all('li')
            stats_dict = {
                'email_title': email_title,
                'open_rate': stats[0].find('span', class_='percent').get_text(strip=True),
                'click_rate': stats[1].find('span', class_='percent').get_text(strip=True),
                'sends': stats[2].find('span', class_='percent').get_text(strip=True),
                'unsubscribes': stats[3].find('span', class_='percent').get_text(strip=True)
            }
            emails_data.append(stats_dict)
        return emails_data

    def fetchSequenceKeyEventsAndRevenue(self):
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="sessionManualAdContent"),  # Emails
                Dimension(name="eventName"),              # Key events
                Dimension(name="sessionManualCampaignName")
            ],
            metrics=[
                Metric(name="purchaseRevenue"),           # Revenue
                Metric(name="eventCount")                 # Key events count
            ],
            date_ranges=[{"start_date": "2024-12-09", "end_date": "2024-12-16"}],
            dimension_filter=FilterExpression(
                filter=Filter(
                    field_name="sessionManualCampaignName",
                    string_filter=Filter.StringFilter(value=self.target_campaign)
                )
            )
        )
        response = self.client.run_report(request)
        raw_data = [
            {
                'ad_content': row.dimension_values[0].value,
                'event_name': row.dimension_values[1].value,
                'campaign_name': row.dimension_values[2].value,
                'revenue': float(row.metric_values[0].value),
                'event_count': int(row.metric_values[1].value)
            }
            for row in response.rows
        ]

        summarized_data = {}
        for entry in raw_data:
            email = entry['ad_content']
            if email not in summarized_data:
                summarized_data[email] = {'revenue': 0, 'purchase_count': 0}
            summarized_data[email]['revenue'] += entry['revenue']
            if entry['event_name'] == 'purchase':
                summarized_data[email]['purchase_count'] += entry['event_count']

        return [
            {
                'email': email,
                'revenue': data['revenue'],
                'purchase_count': data['purchase_count']
            }
            for email, data in summarized_data.items()
        ]



welcome_sequence_fetcher = WelcomeSequence()
print(welcome_sequence_fetcher.extractEmailsData())
print("\n ----------------------------------------------------------------------- \n")
print(welcome_sequence_fetcher.fetchSequenceKeyEventsAndRevenue())
