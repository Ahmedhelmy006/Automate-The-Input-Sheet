import pandas as pd
import os
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, Dimension, Metric

class FetchNboTrafficSource:
    def __init__(self):
        load_dotenv(dotenv_path="D:\Automate the Inputsheet\enviromental_variables.env")
        self.client = BetaAnalyticsDataClient.from_service_account_file(os.getenv('json_key_path'))
        self.property_id = os.getenv('property_id')

    def fetchTrafficSource(self):
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="sessionSource"),
                Dimension(name="sessionMedium")
            ],
            metrics=[Metric(name="sessions")],
            date_ranges=[{"start_date": "2024-12-08", "end_date": "2024-12-16"}]
        )
        response = self.client.run_report(request)
        data = [
            {
                'source': row.dimension_values[0].value,
                'medium': row.dimension_values[1].value,
                'sessions': int(row.metric_values[0].value)
            }
            for row in response.rows
        ]
        return self.formatTrafficSource(data)

    def formatTrafficSource(self, data):
        df = pd.DataFrame(data)
        df['source_medium'] = df.apply(
            lambda x: self.categorize_source(x['source'], x['medium']), axis=1
        )
        pivot = df.pivot_table(values='sessions', columns='source_medium', aggfunc='sum', fill_value=0)
        pivot['Total'] = pivot.sum(axis=1)
        return pivot.T.reset_index()

    def categorize_source(self, source, medium):
        if medium == '(none)' and source == '(direct)':
            return 'Direct'
        if 'organic' in medium:
            return 'Organic Search'
        if 'social' in medium or 'linkedin' in source or 'facebook' in source:
            return 'Organic Social'
        if 'email' in medium:
            return 'Email'
        if 'referral' in medium:
            return 'Referral'
        if 'video' in medium:
            return 'Video'
        return 'Unassigned'

fetch_nbo_traffic_source = FetchNboTrafficSource()
print(fetch_nbo_traffic_source.fetchTrafficSource())
