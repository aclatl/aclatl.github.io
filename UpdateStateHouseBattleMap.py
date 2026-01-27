#!/usr/bin/env python3
"""
Datawrapper Chart Auto-Updater
Fetches data from Google Sheets and updates/republishes a Datawrapper chart.
"""

import os
import requests
from datetime import datetime

# Configuration from environment variables
DATAWRAPPER_API_KEY = os.environ.get('DATAWRAPPER_API_KEY')
CHART_ID = os.environ.get('DATAWRAPPER_CHART_ID', 'kg7Xj')
GOOGLE_SHEET_URL = os.environ.get('GOOGLE_SHEET_URL')

def get_google_sheet_csv(sheet_url: str) -> str:
    """
    Convert a Google Sheets URL to its CSV export URL and fetch the data.
    """
    # Extract the sheet ID from the URL
    # Format: https://docs.google.com/spreadsheets/d/SHEET_ID/edit...
    if '/d/' in sheet_url:
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    else:
        raise ValueError("Invalid Google Sheets URL format")
    
    # Construct the CSV export URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    response = requests.get(csv_url)
    response.raise_for_status()
    
    return response.text


def update_chart_data(api_key: str, chart_id: str, csv_data: str) -> None:
    """
    Upload new data to a Datawrapper chart.
    """
    url = f"https://api.datawrapper.de/v3/charts/{chart_id}/data"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "text/csv"
    }
    
    response = requests.put(url, headers=headers, data=csv_data)
    response.raise_for_status()
    
    print(f"✓ Chart data updated successfully (Status: {response.status_code})")


def update_chart_metadata(api_key: str, chart_id: str) -> None:
    """
    Update the chart's metadata with a timestamp.
    """
    url = f"https://api.datawrapper.de/v3/charts/{chart_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p UTC")
    
    payload = {
        "metadata": {
            "annotate": {
                "notes": f"Last updated: {timestamp}"
            }
        }
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    response.raise_for_status()
    
    print(f"✓ Chart metadata updated with timestamp: {timestamp}")


def publish_chart(api_key: str, chart_id: str) -> str:
    """
    Publish the chart to make changes live.
    """
    url = f"https://api.datawrapper.de/v3/charts/{chart_id}/publish"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    
    result = response.json()
    public_url = result.get('data', {}).get('publicUrl', 'URL not available')
    
    print(f"✓ Chart published successfully!")
    print(f"  Public URL: {public_url}")
    
    return public_url


def main():
    """
    Main function to orchestrate the update process.
    """
    print("=" * 50)
    print("Datawrapper Chart Auto-Update")
    print("=" * 50)
    
    # Validate environment variables
    if not DATAWRAPPER_API_KEY:
        raise ValueError("DATAWRAPPER_API_KEY environment variable is required")
    if not GOOGLE_SHEET_URL:
        raise ValueError("GOOGLE_SHEET_URL environment variable is required")
    
    print(f"\nChart ID: {CHART_ID}")
    print(f"Google Sheet: {GOOGLE_SHEET_URL[:50]}...")
    print()
    
    # Step 1: Fetch data from Google Sheets
    print("Step 1: Fetching data from Google Sheets...")
    csv_data = get_google_sheet_csv(GOOGLE_SHEET_URL)
    print(f"✓ Retrieved {len(csv_data)} bytes of data")
    
    # Step 2: Upload data to Datawrapper
    print("\nStep 2: Uploading data to Datawrapper...")
    update_chart_data(DATAWRAPPER_API_KEY, CHART_ID, csv_data)
    
    # Step 3: Update metadata with timestamp
    print("\nStep 3: Updating chart metadata...")
    update_chart_metadata(DATAWRAPPER_API_KEY, CHART_ID)
    
    # Step 4: Publish the chart
    print("\nStep 4: Publishing chart...")
    public_url = publish_chart(DATAWRAPPER_API_KEY, CHART_ID)
    
    print("\n" + "=" * 50)
    print("Update complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
