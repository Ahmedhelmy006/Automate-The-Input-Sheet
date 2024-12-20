from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, Dimension, Metric, Filter, FilterExpression
)
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="D:\Automate the Inputsheet\enviromental_variables.env")

# Initialize the GA4 client using the JSON key file
client = BetaAnalyticsDataClient.from_service_account_file(os.getenv('json_key_path'))

# Define the GA4 property ID
property_id = os.getenv('property_id')

# Define the campaign name to filter (replace with your target campaign)
target_campaign = os.getenv('target_campaign')

# Create the report request with a filter
request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[
        Dimension(name="sessionManualAdContent"),   # email_1, email_2, etc.
        Dimension(name="sessionManualCampaignName") # Campaign name
    ],
    metrics=[
        Metric(name="purchaseRevenue")  # Total revenue per item
    ],
    date_ranges=[{"start_date": "2024-01-01", "end_date": "2024-12-16"}],
    dimension_filter=FilterExpression(
        filter=Filter(
            field_name="sessionManualCampaignName",  # Field to filter on
            string_filter=Filter.StringFilter(value=target_campaign)
        )
    )
)

# Fetch the report
response = client.run_report(request)

# Print the results
print("Ad Content | Campaign Name | Revenue")
print("-------------------------------------")
for row in response.rows:
    ad_content = row.dimension_values[0].value
    campaign_name = row.dimension_values[1].value
    revenue = row.metric_values[0].value
    print(f"{ad_content} | {campaign_name} | {revenue}")
