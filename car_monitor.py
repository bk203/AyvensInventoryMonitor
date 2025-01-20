import requests
import json
from datetime import datetime
import os
import glob
from typing import Dict, List, Any
from telegram_notifier import TelegramNotifier


class CarInventoryMonitor:
    def __init__(self, telegram_bot_token: str, telegram_chat_id: str):
        self.base_url = "https://www.ayvens.com/api2/cars/queries/groups/"
        self.headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'origin': 'https://www.ayvens.com',
            'x-lpd-countrycode': 'NL',
            'x-lpd-locale': 'nl-NL'
        }
        self.params = {
            'limit': -1,
            'sorting': 'ranking-asc',
            'scope': 'business',
            'state': 'zo goed als nieuw,occasion',
            'tenantId': 'ayvens'
        }
        self.payload = {
            "code": "makemodel",
            "name": "makemodel",
            "values": []
        }
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.telegram = TelegramNotifier(telegram_bot_token, telegram_chat_id)

    def fetch_current_inventory(self):
        """Fetch current inventory data from the API"""
        try:
            response = requests.put(
                self.base_url,
                headers=self.headers,
                params=self.params,
                json=self.payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching inventory: {e}")
            return None

    def save_inventory(self, data):
        """Save inventory data to a JSON file with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'inventory_{timestamp}.json'

        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return filepath
        except Exception as e:
            print(f"Error saving inventory: {e}")
            return None

    def get_most_recent_file(self, exclude_file=None):
        """Find the most recent inventory file, excluding the specified file"""
        pattern = os.path.join(self.data_dir, 'inventory_*.json')
        files = glob.glob(pattern)

        if exclude_file:
            files = [f for f in files if f != exclude_file]

        if not files:
            return None

        return max(files, key=os.path.getctime)

    def load_previous_inventory(self, current_file):
        """Load the most recent previous inventory data"""
        most_recent = self.get_most_recent_file(exclude_file=current_file)
        if not most_recent:
            print("No previous inventory files found")
            return None

        try:
            with open(most_recent, 'r') as f:
                print(f"Loading previous inventory from: {most_recent}")
                return json.load(f)
        except Exception as e:
            print(f"Error loading previous inventory: {e}")
            return None

    def compare_inventories(self, previous_data, current_data):
        """Compare previous and current inventory data"""
        if not previous_data or not current_data:
            return [], []

        previous_groups = previous_data.get('groups', [])
        current_groups = current_data.get('groups', [])

        # Create dictionaries with make+model as key for easy comparison
        previous_dict = {f"{g['make']}_{g['model']}": g for g in previous_groups}
        current_dict = {f"{g['make']}_{g['model']}": g for g in current_groups}

        # Find new entries
        new_entries = []
        for key, current_group in current_dict.items():
            if key not in previous_dict:
                new_entries.append({
                    'type': 'new_model',
                    'make': current_group['make'],
                    'model': current_group['model'],
                    'numberOfTrimlines': current_group['numberOfTrimlines']
                })

        # Find changed entries
        changed_entries = []
        for key in set(previous_dict.keys()) & set(current_dict.keys()):
            prev_group = previous_dict[key]
            curr_group = current_dict[key]

            if prev_group['numberOfTrimlines'] != curr_group['numberOfTrimlines']:
                changed_entries.append({
                    'type': 'trimlines_changed',
                    'make': curr_group['make'],
                    'model': curr_group['model'],
                    'previous_trimlines': prev_group['numberOfTrimlines'],
                    'current_trimlines': curr_group['numberOfTrimlines']
                })

        # Find removed entries
        removed_entries = []
        for key, prev_group in previous_dict.items():
            if key not in current_dict:
                removed_entries.append({
                    'type': 'removed_model',
                    'make': prev_group['make'],
                    'model': prev_group['model'],
                    'numberOfTrimlines': prev_group['numberOfTrimlines']
                })

        return {
            'new': new_entries,
            'changed': changed_entries,
            'removed': removed_entries
        }

    def notify_changes(self, changes: Dict[str, List[Any]]) -> None:
        """Send notification about changes via Telegram"""
        if any(changes.values()):  # Only send if there are actual changes
            message = self.telegram.format_changes_message(changes)
            self.telegram.send_message(message)