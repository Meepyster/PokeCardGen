import requests
import json
from random import randint
from dotenv import load_dotenv
import os
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="Pokemon 10 Card Gen",
    contact={
        "name": "Meepyster",
        "url": "https://github.com/Meepyster/PokeCardGen",
    },
    description="""
## Introduction to this API

This API uses the PokeAPI and PokeTCG API to get random pokemon cards.
https://pokeapi.co/
https://pokemontcg.io/
""",
)

load_dotenv()
api_key = os.getenv("POKETCG_API_KEY")  # Replace with actual env var name
headers = {"x-api-key": api_key}


@app.get("/get-10-cards")
def get10Cards():
    totalValue = 0
    realWorldtotalValue = 0
    pulled_cards = []
    successful_draws = 0

    while successful_draws < 10:
        try:
            pokemon_id = randint(1, 1025)
            url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            name = data["forms"][0]["name"]
            base_exp = data["base_experience"]

            urlTCG = f"https://api.pokemontcg.io/v2/cards/?q=name:{name}"
            responseTCG = requests.get(urlTCG, headers=headers)
            responseTCG.raise_for_status()
            dataTCG = responseTCG.json()

            cards = dataTCG.get("data", [])
            if not cards:
                continue

            card = cards[randint(0, len(cards) - 1)]
            value = 0
            match card.get("rarity", "Unknown"):
                case "Unknown":
                    value = round(base_exp / 150, 2)
                case "Common":
                    value = 0.5
                case "Uncommon":
                    value = 0.8
                case "Rare":
                    value = 1.3
                case "Double Rare":
                    value = 2
                case "Rare Holo":
                    value = 1.5
                case "Rare BREAK":
                    value = 20
                case "Rare Holo V":
                    value = 2
                case "Rare Holo EX":
                    value = 3.20
                case "Rare Holo GX":
                    value = 2.60
                case "Ultra Rare":
                    value = 5
                case "Rare Ultra":
                    value = 10.00
                case "Rare Holo VMAX":
                    value = 14.00
                case "Rare Prime":
                    value = 4.20
                case "Amazing Rare":
                    value = 5.00
                case "Rare Holo LV.X":
                    value = 6.00
                case "Rare Shiny":
                    value = 2.00
                case "Rare Shiny GX":
                    value = 8.00
                case "Rare Rainbow":
                    value = 12.00
                case "Rare Prism Star":
                    value = 18.00
                case "Rare Holo Star":
                    value = 20.00
                case "Rare Holo VSTAR":
                    value = 15.00
                case "LEGEND":
                    value = 25.00
                case "Rare Secret":
                    value = 22.00
                case "Promo":
                    value = round(base_exp / 55, 2)
                case "Illustration Rare":
                    value = round(base_exp / 30, 2)
                case "Special Illustration Rare":
                    value = 20
                case "Trainer Gallery Rare":
                    value = 25
                case _:
                    value = round(base_exp / 100, 2)
            subtypes = card.get("subtypes", [])
            prefix = ""
            suffix = ""
            for subtype in subtypes:
                match subtype.lower():
                    case "ex":
                        value *= 2
                        value = round(value, 2)
                        suffix = " EX"
                    case "gx":
                        value *= 2.1
                        value = round(value, 2)
                        suffix = " GX"
                        # prefix = subtype
                    case "v":
                        value *= 2.5
                        value = round(value, 2)
                        # prefix = subtype
                    case "tag team":
                        value *= 5.0
                        value = round(value, 2)
                        prefix = " Tag Team"
                    case "mega":
                        prefix = " Mega"
                        value *= 5
                        value = round(value, 2)
                        # prefix = subtype
                    case "vmax":
                        value *= 2.5
                        value = round(value, 2)
                        # prefix = subtype
                    case "vstar":
                        value *= 2.5
                        value = round(value, 2)
                        # prefix = subtype
                    case "legend":
                        value *= 8.0
                        value = round(value, 2)
                    case "tera":
                        value *= 5.0
                        value = round(value, 2)
                    case "sp":
                        value *= 1.3
                        value = round(value, 2)
                    case _:
                        continue
            totalValue += round(value, 2)
            if not card.get("tcgplayer", []):
                marketValue = 0
                print("\n\n NONE \n\n")
            else:
                res = next(iter(card.get("tcgplayer")["prices"]))
                marketValue = card.get("tcgplayer")["prices"][res]["market"]
                print(f"\n\n {marketValue} \n\n ")
            realWorldtotalValue += marketValue
            pulled_cards.append(
                {
                    "card_title": f"{card.get("rarity", "Unknown")}{prefix} {name.capitalize()}{suffix}",
                    "name": name,
                    "base_experience": base_exp,
                    "card_image": card["images"]["large"],
                    "rarity": card.get("rarity", "Unknown"),
                    "subtypes": subtypes,
                    "value": value,
                    "real-market-value": marketValue,
                    "discrepancy-ratio": round(marketValue / value, 2),
                }
            )

            successful_draws += 1
            time.sleep(0.2)

        except Exception as e:
            print(f"⚠️ Error occurred: {e}")
            continue

    return {
        "cards": pulled_cards,
        "total_value": round(totalValue, 2),
        "realworld_total_value": round(realWorldtotalValue, 2),
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
