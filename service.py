import json
import random
import os


def load_set(set_id, base_folder="sets", use_subfolder=True):
    folder = os.path.join(base_folder, set_id)
    card_file = os.path.join(folder, "cards.json")
    config_file = os.path.join(folder, "config.json")

    with open(card_file, "r") as f:
        cards = json.load(f)
    with open(config_file, "r") as f:
        config = json.load(f)

    # Group cards by rarity
    cards_by_rarity = {}
    for card in cards:
        rarity = card.get("rarity", "Unknown")
        cards_by_rarity.setdefault(rarity, []).append(card)

    return cards_by_rarity, config


def upgrade_card(card, set_config, cards_by_rarity):
    base_rarity = card.get("rarity", "Unknown")
    upgrade_options = set_config.get("upgrade_table", {}).get(base_rarity, {})

    # Exclusive-first-success: attempt higher-probability upgrades first
    for target_rarity, chance in sorted(upgrade_options.items(), key=lambda x: -x[1]):
        if random.random() < chance and cards_by_rarity.get(target_rarity):
            print("\nUPGRADE TO: ", target_rarity, "\n")
            return random.choice(cards_by_rarity[target_rarity])
    card["card_title"] = card["name"]
    return card


def open_pack(set_id, base_folder="sets", use_subfolder=True):
    cards_by_rarity, set_config = load_set(set_id, base_folder, use_subfolder)
    pack = []

    # Base slots
    for rarity, count in set_config.get("pack_structure", {}).items():
        if rarity == "RareSlot":
            continue
        for _ in range(count):
            base_card = random.choice(cards_by_rarity[rarity])
            pack.append(upgrade_card(base_card, set_config, cards_by_rarity))

    # Rare slot
    rare_rarity = random.choices(
        list(set_config["rare_slot_weights"].keys()),
        weights=list(set_config["rare_slot_weights"].values()),
    )[0]
    rare_card = random.choice(cards_by_rarity[rare_rarity])
    pack.append(upgrade_card(rare_card, set_config, cards_by_rarity))

    return pack
