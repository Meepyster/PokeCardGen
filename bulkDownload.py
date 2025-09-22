# bulk_download_cards.py
import requests
import json
import sys
import traceback
from dotenv import load_dotenv
import os

url = "https://api.pokemontcg.io/v2/cards?pageSize=250"
all_cards = []
page = 1
load_dotenv()
api_key = os.getenv("POKETCG_API_KEY")
headers = {"x-api-key": api_key}

try:
    while True:
        print(f"Fetching page {page}...")
        resp = requests.get(f"{url}&page={page}", headers=headers)
        resp.raise_for_status()
        data = resp.json()
        cards = data.get("data", [])

        if not cards:
            print("No more cards found, stopping.")
            break

        all_cards.extend(cards)
        page += 1

        # Stop if we've collected everything
        if len(cards) < 250:
            print("Last page reached.")
            break

except Exception as e:
    print(f"❌ Error while fetching page {page}: {e}")
    traceback.print_exc(file=sys.stdout)

finally:
    # Always dump what we got so far
    print(f"💾 Saving {len(all_cards)} cards to cards.json")
    with open("cards.json", "w", encoding="utf-8") as f:
        json.dump(all_cards, f, ensure_ascii=False, indent=2)
    print("Done")
