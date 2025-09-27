import json
import os
from pathlib import Path

base_folder = "sets"
set_id = "sv8pt5"


folder = os.path.join(base_folder, set_id)
card_file = os.path.join(folder, "cards.json")


def clean_card(card: dict) -> dict:
    return {
        "id": card.get("id", ""),
        "card_title": card.get("name", ""),
        "name": card.get("name", ""),
        "base_experience": "1000",
        "card_image": card.get("images", {}).get("large", ""),
        "rarity": card.get("rarity", "Unknown"),
        "subtypes": card.get("subtypes", []),
        "value": float(card.get("value", 0.0)),
        "real_market_value": float(card.get("value", 0.0)),
        "discrepancy_ratio": 1.0,
    }


def clean_json_file(input_file: str, output_file: str):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_cards = [clean_card(card) for card in data]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_cards, f, indent=2, ensure_ascii=False)


clean_json_file(card_file, "sv8pt5_cards_clean.json")
