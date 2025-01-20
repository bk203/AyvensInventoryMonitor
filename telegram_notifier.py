import requests
from datetime import datetime
from typing import Dict, List, Any


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, message: str) -> bool:
        """Send a message via Telegram"""
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    def format_changes_message(self, changes: Dict[str, List[Any]]) -> str:
        """Format the changes into a readable Telegram message"""
        message_parts = ["<b>🚗 Car Inventory Update</b>\n"]

        if changes['new']:
            message_parts.append("\n<b>🆕 New Models:</b>")
            for entry in changes['new']:
                message_parts.append(
                    f"• {entry['make']} {entry['model']} "
                    f"(Trimlines: {entry['numberOfTrimlines']})"
                )

        if changes['changed']:
            message_parts.append("\n<b>📝 Changed Trimlines:</b>")
            for entry in changes['changed']:
                message_parts.append(
                    f"• {entry['make']} {entry['model']}: "
                    f"{entry['previous_trimlines']} → {entry['current_trimlines']}"
                )

        if changes['removed']:
            message_parts.append("\n<b>❌ Removed Models:</b>")
            for entry in changes['removed']:
                message_parts.append(
                    f"• {entry['make']} {entry['model']} "
                    f"(Had {entry['numberOfTrimlines']} trimlines)"
                )

        if not any(changes.values()):
            message_parts.append("\nNo changes detected in inventory")

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message_parts.append(f"\n\nUpdate time: {timestamp}")

        return "\n".join(message_parts)