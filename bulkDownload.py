# bulk_download_cards.py
import requests
import json

url = "https://api.pokemontcg.io/v2/cards?pageSize=250"
all_cards = []
page = 1

while True:
    print(f"Fetching page {page}...")
    resp = requests.get(f"{url}&page={page}")
    resp.raise_for_status()
    data = resp.json()
    cards = data.get("data", [])
    print(cards)
    if not cards:
        break

    all_cards.extend(cards)
    page += 1

    # Stop if we've collected everything
    if len(cards) < 250:
        break

print(f"✅ Downloaded {len(all_cards)} cards")

with open("cards.json", "w", encoding="utf-8") as f:
    json.dump(all_cards, f, ensure_ascii=False, indent=2)
