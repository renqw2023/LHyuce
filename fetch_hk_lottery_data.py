#!/usr/bin/env python3
"""
Script to fetch HK lottery data (lotteryType=1) from pages 1-6 and save to JSON file
"""

import requests
import json
import time
from datetime import datetime

def fetch_hk_lottery_page(page_num, page_size=10):
    """Fetch HK lottery data for a specific page"""
    url = f"https://49208.com/unite49/h5/lottery/search?pageNum={page_num}&pageSize={page_size}&lotteryType=1&year=2025&sort=1"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return None

def main():
    """Main function to fetch all pages dynamically and save HK lottery data"""
    page_size = 10

    # Step 1: Fetch the first page to determine the total number of pages
    print("Determining total number of pages for Hong Kong data...")
    first_page_data = fetch_hk_lottery_page(1, page_size)
    total_pages = 0

    if first_page_data and first_page_data.get('success'):
        data_node = first_page_data.get('data', {})
        if 'pages' in data_node:
            total_pages = data_node['pages']
        elif 'total' in data_node:
            total_records = data_node['total']
            total_pages = (total_records + page_size - 1) // page_size
        
        if total_pages > 0:
            print(f"Success. Total pages found: {total_pages}")
        else:
            print("Warning: Could not determine total pages. Falling back to a default of 10 pages.")
            total_pages = 10
    else:
        print("Error: Failed to fetch first page. Aborting.")
        return

    all_data = {
        "dataSource": "https://49208.com/unite49/h5/lottery/search",
        "parameters": {
            "lotteryType": 1,
            "year": 2025,
            "sort": 1,
            "pageRange": f"1-{total_pages}",
            "description": "Hong Kong Lottery Data"
        },
        "collectionTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalRecords": [],
        "pages": []
    }
    
    print(f"Starting to fetch HK lottery data from pages 1-{total_pages}...")
    
    for page_num in range(1, total_pages + 1):
        # If we are on the first page, we can reuse the data we already fetched
        if page_num == 1 and first_page_data:
            page_data = first_page_data
        else:
            print(f"Fetching page {page_num}...")
            page_data = fetch_hk_lottery_page(page_num, page_size)
        
        if page_data and page_data.get('success'):
            all_data["pages"].append({
                "pageNum": page_num,
                "data": page_data["data"]
            })
            if "recordList" in page_data["data"]:
                all_data["totalRecords"].extend(page_data["data"]["recordList"])
            
            print(f"Page {page_num} fetched successfully - {len(page_data['data'].get('recordList', []))} records")
        else:
            print(f"Failed to fetch page {page_num}")
        
        time.sleep(1)
    
    # Save all data to file
    output_file = "HK2025_lottery_data_complete.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nHK lottery data collection complete!")
    print(f"Total records collected: {len(all_data['totalRecords'])}")
    print(f"Data saved to: {output_file}")

if __name__ == "__main__":
    main()
