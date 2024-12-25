import pandas as pd
import os
import sys
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, Dimension, Metric
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.date_to_serial import DateToSerial

class FetchNboTrafficSource:
    def __init__(self):
        load_dotenv(dotenv_path="D:\Automate the Inputsheet\enviromental_variables.env")
        self.service_account_file = os.getenv('json_key_path')
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/analytics.readonly'
        ]
        self.credentials = Credentials.from_service_account_file(self.service_account_file, scopes=self.scopes)
        self.client = BetaAnalyticsDataClient(credentials=self.credentials)
        self.property_id = os.getenv('property_id')

    def get_date_range(self):
        """
        Calculate the start date (first Monday before the previous Sunday)
        and the end date (previous Sunday).
        """
        today = datetime.now()

        # Calculate previous Sunday
        end_date = today - timedelta(days=today.weekday() + 1)

        # Calculate first Monday before the previous Sunday
        start_date = end_date - timedelta(days=6)

        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


    def fetchTrafficAcquisition(self):
        """
        Fetch traffic data from the Traffic Acquisition predefined report in Google Analytics.
        Include the serial date as a separate column for all entries.
        """
        # Get dynamic date range
        start_date, end_date = self.get_date_range()
        print(f"Fetching data from {start_date} to {end_date}")

        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="sessionDefaultChannelGrouping"),  # Primary channel grouping
            ],
            metrics=[
                Metric(name="sessions"),                         # Total sessions
                Metric(name="engagedSessions"),                  # Engaged sessions
                Metric(name="engagementRate"),                   # Engagement rate
                Metric(name="eventCount"),                       # Event count
                Metric(name="conversions"),                      # Key events
                Metric(name="totalRevenue"),                     # Total revenue
            ],
            date_ranges=[{"start_date": start_date, "end_date": end_date}]
        )
        response = self.client.run_report(request)

        today_date = datetime.now().strftime("%Y/%m/%d")
        serial_date = DateToSerial.dateToSerial(today_date)

        # Extract data from the response
        data = [
            {
                'Date': serial_date,
                'Channel Grouping': row.dimension_values[0].value,
                'Sessions': int(row.metric_values[0].value),
                'Engaged Sessions': int(row.metric_values[1].value),
                'Engagement Rate': f"{float(row.metric_values[2].value) * 100:.2f}",
                'Event Count': int(row.metric_values[3].value),
                'Key Events': int(row.metric_values[4].value),
                'Total Revenue': f"{float(row.metric_values[5].value):,.2f}",
            }
            for row in response.rows
        ]

        return pd.DataFrame(data)

    def write_to_google_sheet(self, data_frame, spreadsheet_id, tab_name):
        """
        Append data to a specific Google Sheet tab.
        """
        service = build('sheets', 'v4', credentials=self.credentials)
        sheet = service.spreadsheets()

        # Fetch existing data to find the last row in the correct tab
        range_name = f"{tab_name}!A1:Z"
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        start_row = len(values) + 1  # Calculate the next empty row

        # Prepare data for appending
        data = [data_frame.columns.tolist()] if start_row == 1 else []  # Include headers only if the tab is empty
        data += data_frame.values.tolist()

        # Write to the sheet starting at the next empty row
        range_to_write = f"{tab_name}!A{start_row}"
        print(f"Writing to range: {range_to_write}")

        request = sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=range_to_write,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": data}
        )
        response = request.execute()
        print(f"Data appended successfully to tab '{tab_name}'.")

if __name__ == "__main__":
    fetch_nbo_traffic_source = FetchNboTrafficSource()

    # Fetch the data from Google Analytics
    traffic_data = fetch_nbo_traffic_source.fetchTrafficAcquisition()

    # Print the fetched data for verification
    print(traffic_data)

    # Write data to Google Sheets
    SPREADSHEET_ID = "1JHj2_sxTUJZ6Oar5oIIUv6JatrqZ5qQ3DS3eVOXEnlo"
    TAB_NAME = "NBO Traffic Acquisitions"
    fetch_nbo_traffic_source.write_to_google_sheet(traffic_data, SPREADSHEET_ID, TAB_NAME)
