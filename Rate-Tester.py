import json
import random
import os
from collections import Counter

## JUST CHANGE THESE VALUES --------------------------------
N = 1000000
set_id = "sv8pt5"
## ---------------------------------------------------------

base_folder = "sets"
folder = os.path.join(base_folder, set_id)
config_file_path = os.path.join(folder, "config.json")

# Load config.json into a Python dict
with open(config_file_path, "r") as f:
    config = json.load(f)


def weighted_choice(weight_dict):
    """Pick one key from a dict of weights."""
    total = sum(weight_dict.values())
    r = random.uniform(0, total)
    upto = 0
    for k, w in weight_dict.items():
        if upto + w >= r:
            return k
        upto += w
    return k


def apply_upgrade(base_rarity, upgrades):
    """Try upgrading a card based on upgrade_table."""
    if base_rarity not in upgrades:
        return base_rarity
    for target, chance in upgrades[base_rarity].items():
        if random.random() < chance:
            return target
    return base_rarity


def open_pack(config):
    """Simulate opening one booster pack."""
    pulls = []

    # Commons
    for _ in range(config["pack_structure"]["Common"]):
        rarity = "Common"
        rarity = apply_upgrade(rarity, config["upgrade_table"])
        pulls.append(rarity)

    # Uncommons
    for _ in range(config["pack_structure"]["Uncommon"]):
        rarity = "Uncommon"
        rarity = apply_upgrade(rarity, config["upgrade_table"])
        pulls.append(rarity)

    # Rare Slot
    rarity = weighted_choice(config["rare_slot_weights"])
    rarity = apply_upgrade(rarity, config["upgrade_table"])
    pulls.append(rarity)

    return pulls


def simulate_packs(n_packs, config):
    counts = Counter()
    for _ in range(n_packs):
        pulls = open_pack(config)
        counts.update(pulls)
    return counts


# Run simulation
results = simulate_packs(N, config)

# Print results
print(f"Simulated {N} packs:")
for rarity in config["rarities"]:
    count = results[rarity]
    rate = count / N
    one_in_x = (1 / rate) if rate > 0 else float("inf")
    print(f"{rarity:25} {count:6} pulls  → {rate:.4%} per pack  (~1 in {one_in_x:.1f})")
