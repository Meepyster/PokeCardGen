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
        "url": "https://example.com",
    },
    description="""
## Introduction to this API

This API uses the PokeAPI and PokeTCG API to get random pokemon cards.
""",
)

load_dotenv()
api_key = os.getenv("POKETCG_API_KEY")  # Replace with actual env var name
headers = {
    "x-api-key": api_key
}


@app.get("/get-10-cards")
def get10Cards():
    pulled_cards = []
    successful_draws = 0

    while successful_draws < 10:
        try:
            pokemon_id = randint(1, 1000)
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

            pulled_cards.append({
                "name": name,
                "base_experience": base_exp,
                "card_image": card["images"]["large"],
                "rarity": card.get("rarity", "Unknown")
            })

            successful_draws += 1
            time.sleep(0.2)

        except Exception as e:
            print(f"⚠️ Error occurred: {e}")
            continue

    return {"cards": pulled_cards}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)