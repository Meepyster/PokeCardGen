import json
import os
import random

# Paths
set_id = "me1"
base_folder = "sets"
folder = os.path.join(base_folder, set_id)
cards_file_path = os.path.join(folder, "cards.json")

# Load cards
with open(cards_file_path, "r") as f:
    cards = json.load(f)

# Define rarity → price ranges
rarity_price_ranges = {
    "Common": (0.1, 0.5),
    "Uncommon": (0.1, 0.5),
    "Rare": (0.5, 1.0),
    "Double Rare": (1.0, 4.0),
    # Anything else will be left for manual pricing
}

# Add prices
for card in cards:
    rarity = card.get("rarity", "Unknown")
    if rarity in rarity_price_ranges:
        low, high = rarity_price_ranges[rarity]
        card["value"] = round(random.uniform(low, high), 2)
    else:
        card["value"] = None  # placeholder, set manually later

# Save back into the same file (or new one if you want)
output_path = os.path.join(folder, "cards_priced.json")
with open(output_path, "w") as f:
    json.dump(cards, f, indent=2)

print(f"Saved priced cards to {output_path}")
