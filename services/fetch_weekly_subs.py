import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from utils.GoogleFormsSubmitter import GoogleFormsSubmitter

# Load environment variables
load_dotenv(dotenv_path="D:\Automate the Inputsheet\enviromental_variables.env")
API_KEY = os.getenv('KIT_V4_API_KEY')

# Weekly Form Fields
form_url = os.getenv('weekly_subs_form_url')
form_fields= {
    'Number of subs' : 'entry.464579160',
    'Net New Subs' : 'entry.1240621522', 
    'Weekly Cancelations' : 'entry.163503538',
    'Total Number of Subs' : 'entry.1332978114'
}
def pull_subs(key=API_KEY):
    headers = {'Accept': 'application/json', 'X-Kit-Api-Key': key}
    today = datetime.now() + timedelta(hours=1)  # CET adjustment
    start_date = (today - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00+01:00")
    end_date = (today - timedelta(days=1)).strftime("%Y-%m-%dT23:59:59+01:00")

    params = {"starting": start_date, "ending": end_date}
    r = requests.get('https://api.kit.com/v4/account/growth_stats', headers=headers, params=params)
    print(r.json())
    return r.json()

def submit_weekly_data():
    weekly_data = pull_subs()

    weekly_subs_count = weekly_data.get('stats', {}).get('subscribers', 0)
    weekly_cancellation = weekly_data.get('stats', {}).get('cancellations', 0)
    weekly_net_new_subs = weekly_data.get('stats', {}).get('net_new_subscribers', 0)
    weekly_new_subs = weekly_data.get('stats', {}).get('new_subscribers', 0)

    form_data = {
        "Number of subs": weekly_new_subs,
        "Net New Subs": weekly_net_new_subs,
        'Weekly Cancelations': weekly_cancellation,
        "Total Number of Subs": weekly_subs_count
    }

    GoogleFormsSubmitter(form_url, form_fields).submit_data(form_data)
    print("Weekly data submitted successfully!")

# Execute weekly submission
submit_weekly_data()
