from datetime import datetime

import requests
from xml.etree import ElementTree
from models.feed_model import save_offer, get_offer_by_id, save_change

FEED_URL = "" #secret
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
COOKIES = {
    #secret
}

def fetch_feed():
    try:
        response = requests.get(FEED_URL, headers=HEADERS, cookies=COOKIES)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Помилка завантаження фіду: {e}")
        return None

def parse_and_store_feed(feed_data):
    try:
        tree = ElementTree.fromstring(feed_data)
        changes = []
        for offer in tree.findall(".//offer"):
            offer_data = {
                "id": offer.get("id"),
                "name": offer.findtext("name"),
                "price": offer.findtext("price"),
                "vendor": offer.findtext("vendor"),
                "quantity_in_stock": offer.findtext("quantity_in_stock"),
                "picture": offer.findtext("picture"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Додаємо поточний час
            }
            existing_offer = get_offer_by_id(offer_data['id'])
            if existing_offer:
                changes += track_changes(offer_data, existing_offer)
            save_offer(offer_data)
        for change in changes:
            save_change(change)
        return changes
    except ElementTree.ParseError as e:
        print(f"Помилка парсингу XML: {e}")
        return []

def track_changes(offer_data, existing_offer):
    changes = []
    fields_to_check = ['price', 'quantity_in_stock']  # Поля для перевірки змін

    for field in fields_to_check:
        old_value = str(existing_offer[field])
        new_value = str(offer_data[field])
        if old_value != new_value:
            changes.append({
                "offer_id": offer_data["id"],
                "field": field,
                "old_value": old_value,
                "new_value": new_value,
            })
    return changes
