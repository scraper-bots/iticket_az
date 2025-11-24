#!/usr/bin/env python3
"""
iTicket.az Event Scraper
Scrapes all events from the iticket.az API and saves to CSV
"""

import requests
import csv
import time
from datetime import datetime
from typing import List, Dict, Optional

class ITicketScraper:
    def __init__(self):
        self.base_url = "https://api.iticket.az/en/v5/events"
        self.headers = {
            'accept': 'application/json',
            'authorization': 'Bearer',
            'origin': 'https://iticket.az',
            'referer': 'https://iticket.az/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.all_events = []

    def fetch_page(self, page: int) -> Optional[Dict]:
        """Fetch a single page from the API"""
        params = {
            'client': 'web',
            'page': page
        }

        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            return None

    def is_valid_page(self, data: Dict) -> bool:
        """Check if the page contains valid data"""
        if not data:
            return False

        # Check if response and events exist
        if 'response' not in data or 'events' not in data['response']:
            return False

        events = data['response']['events']

        # Check if data array exists and is not empty
        if 'data' not in events or not events['data']:
            return False

        # Check if from/to pagination fields are null (indicates no data)
        if events.get('from') is None or events.get('to') is None:
            return False

        return True

    def extract_event_data(self, event: Dict) -> Dict:
        """Extract relevant fields from an event"""
        # Venues is an array, get the first one if available
        venues = event.get('venues', [])
        venue = venues[0] if venues else {}

        return {
            'event_id': event.get('id'),
            'title': event.get('title', {}).get('en') if isinstance(event.get('title'), dict) else event.get('title'),
            'slug': event.get('slug'),
            'category_id': event.get('category_id'),
            'category_slug': event.get('category_slug'),
            'age_limit': event.get('age_limit'),
            'min_price': event.get('min_price'),
            'max_price': event.get('max_price'),
            'available_tickets_count': event.get('available_tickets_count'),
            'event_starts_at': event.get('event_starts_at'),
            'event_ends_at': event.get('event_ends_at'),
            'sell_starts_at': event.get('sell_starts_at'),
            'sell_ends_at': event.get('sell_ends_at'),
            'upcoming_mode': event.get('upcoming_mode'),
            'venue_id': venue.get('id'),
            'venue_name': venue.get('name'),
            'venue_phone': venue.get('phone'),
            'venue_mobile': venue.get('mobile'),
            'venue_latitude': venue.get('map_lat'),
            'venue_longitude': venue.get('map_lng'),
            'poster_url': event.get('poster_url'),
            'poster_bg_url': event.get('poster_bg_url'),
            'public_state': event.get('public_state'),
            'web_view_rotate': event.get('web_view_rotate'),
        }

    def scrape_all_pages(self):
        """Scrape all pages until we run out of valid data"""
        page = 1

        print("Starting to scrape iticket.az events...")
        print("-" * 50)

        while True:
            print(f"Fetching page {page}...", end=" ")

            data = self.fetch_page(page)

            if not self.is_valid_page(data):
                print("No more valid data found.")
                break

            events_obj = data['response']['events']
            events = events_obj['data']
            print(f"Found {len(events)} events")

            for event in events:
                self.all_events.append(self.extract_event_data(event))

            # Check if there's a next page
            if not events_obj.get('next_page_url'):
                print("Reached last page.")
                break

            page += 1

            # Be respectful to the API - add a small delay
            time.sleep(0.5)

        print("-" * 50)
        print(f"Total events scraped: {len(self.all_events)}")

    def save_to_csv(self, filename: str = "iticket_events.csv"):
        """Save all events to a CSV file"""
        if not self.all_events:
            print("No events to save!")
            return

        # Get all unique keys from all events
        fieldnames = list(self.all_events[0].keys())

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.all_events)

        print(f"Events saved to {filename}")

def main():
    scraper = ITicketScraper()

    # Scrape all pages
    start_time = time.time()
    scraper.scrape_all_pages()

    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"iticket_events_{timestamp}.csv"
    scraper.save_to_csv(filename)

    elapsed_time = time.time() - start_time
    print(f"Scraping completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
