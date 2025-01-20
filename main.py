from car_monitor import CarInventoryMonitor
import os


def main():
    # Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    monitor = CarInventoryMonitor(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

    # Fetch current inventory
    current_data = monitor.fetch_current_inventory()
    if current_data:
        print(f"Successfully fetched data with {len(current_data.get('groups', []))} groups")

        # Save current inventory with timestamp
        current_file = monitor.save_inventory(current_data)
        if current_file:
            print(f"Data saved to {current_file}")

            # Load most recent previous inventory for comparison
            previous_data = monitor.load_previous_inventory(current_file)
            if previous_data:
                changes = monitor.compare_inventories(previous_data, current_data)

                # Send notifications via Telegram
                monitor.notify_changes(changes)

                # Print changes to console as well
                print(monitor.telegram.format_changes_message(changes))


if __name__ == "__main__":
    main()