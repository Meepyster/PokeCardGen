import requests
import json
from random import randint
from dotenv import load_dotenv
import os
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated
from typing import List, Dict, Optional
import uuid
import service
from models import (
    Trade,
    Card,
    CreateTradeRequest,
    JoinTradeRequest,
    OfferRequest,
    ConfirmRequest,
)
import time

app = FastAPI(
    title="PokeSwift API",
    contact={
        "name": "Meepyster",
        "url": "https://github.com/Meepyster/PokeCardGen",
    },
    description="""
## Introduction to this API

This API uses the PokeAPI and PokeTCG API to get random pokemon cards.
https://pokeapi.co/
https://pokemontcg.io/

This API also powers pokeswift 
""",
)

load_dotenv()
api_key = os.getenv("POKETCG_API_KEY")
headers = {"x-api-key": api_key}

cardDB = {}
trades: Dict[str, Trade] = {}
setCount = {}
setCount["sv8pt5"] = 1000

setCount = {"sv8pt5": 1000}


def auto_increase_setcount(set_id: str, increment: int = 10, interval: int = 60):
    """Increase setCount[set_id] every `interval` seconds by `increment`."""
    while True:
        time.sleep(interval)  # wait N seconds
        setCount[set_id] += increment
        print(f"{set_id} → {setCount[set_id]}")


auto_increase_setcount("sv8pt5")


@app.get("/trades/get-all")
def get_all_trades():
    return trades


@app.post("/trades/{trade_id}/offer", response_model=Trade)
def offer_card(trade_id: str, req: OfferRequest):
    trade = trades.get(trade_id)
    if not trade:
        raise HTTPException(404, "Trade not found")
    if req.user_id == trade.userB:
        trade.cardB = req.cardB
        trade.status = "awaiting_confirmations"
    else:
        raise HTTPException(403, "Only userB can offer card in this step")
    trades[trade_id] = trade
    return trade


@app.post("/trades", response_model=Trade)
def create_trade(req: CreateTradeRequest):
    trade_id = req.cardA.id
    if trade_id in trades:
        raise HTTPException(400, "Trade already exists for this card")

    trade = Trade(
        id=trade_id,
        userA=req.userA,
        cardA=req.cardA,
        confirmations={req.userA: False},
    )
    trades[trade_id] = trade
    return trade


@app.delete("/clear-beta-trade")
def clear_beta_trade():
    cardDB.clear()
    return "ITS DONEZO BUDDY RIPBOZO"


@app.delete("/clear-trade")
def clear_trade():
    trades.clear()
    return "GOODBYE SUCKA"


@app.post("/trades/{trade_id}/join", response_model=Trade)
def join_trade(trade_id: str, req: JoinTradeRequest):
    trade = trades.get(trade_id)
    if not trade:
        raise HTTPException(404, "Trade not found")
    if trade.userB:
        raise HTTPException(400, "Trade already joined")

    trade.userB = req.userB
    trade.confirmations[req.userB] = False
    trade.status = "joined"
    trades[trade_id] = trade
    return trade


@app.post("/trades/{trade_id}/confirm", response_model=Trade)
def confirm_trade(trade_id: str, req: ConfirmRequest):
    trade = trades.get(trade_id)
    if not trade:
        raise HTTPException(404, "Trade not found")
    if req.user_id not in trade.confirmations:
        raise HTTPException(403, "Not a participant")

    trade.confirmations[req.user_id] = True

    if all(trade.confirmations.values()) and trade.cardB:
        trade.status = "completed"
        # -- TODO --
    trades[trade_id] = trade
    return trade


@app.get("/trades/{trade_id}", response_model=Trade)
def get_trade(trade_id: str):
    trade = trades.get(trade_id)
    if not trade:
        raise HTTPException(404, "Trade not found")
    return trade


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
                    value = 4
                case "Rare Holo EX":
                    value = 3.20
                case "Rare Holo GX":
                    value = 2.60
                case "Ultra Rare":
                    value = 5
                case "Hyper Rare":
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
                case "Shiny Rare":
                    value = round(base_exp / 30, 2) + 5
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
                    value = round(base_exp / 30, 2) + 5
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
                    "id": "",
                    "card_title": f"{card.get("rarity", "Unknown")}{prefix} {name.capitalize()}{suffix}",
                    "name": name,
                    "base_experience": base_exp,
                    "card_image": card["images"]["large"],
                    "rarity": card.get("rarity", "Unknown"),
                    "subtypes": subtypes,
                    "value": value,
                    "real_market_value": marketValue,
                    "discrepancy_ratio": round(marketValue / value, 2),
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


@app.post("/postCard")
def postCardForSale(card: Card):
    cardDB[card.id] = card.dict()
    return {
        "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={card.id}"
    }


@app.get("/reveal-db")
def seeAllCards():
    return cardDB


@app.get("/trade-cards/{card_id}")
def getCardForSale(card_id: str):
    if card_id not in cardDB:
        raise HTTPException(status_code=404, detail="Card not found for trade")
    copyCard = cardDB.pop(card_id)
    return copyCard


@app.get("/custom-10-cards")
def getCustomPack():
    totalValue = 0
    realWorldtotalValue = 0
    pulled_cards = []
    successful_draws = 0
    base_exp = 1000
    with open("cards.json", "r", encoding="utf-8") as f:
        cards = json.load(f)
    while successful_draws < 10:
        try:
            if not cards:
                continue
            card = cards[randint(0, 2999)]
            value = 0
            name = card.get("name")
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
                    value = 4
                case "Rare Holo EX":
                    value = 3.20
                case "Rare Holo GX":
                    value = 2.60
                case "Ultra Rare":
                    value = 5
                case "Hyper Rare":
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
                case "Shiny Rare":
                    value = round(base_exp / 30, 2) + 5
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
                    value = round(base_exp / 30, 2) + 5
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
                    "id": str(uuid.uuid4()),
                    "card_title": f"{card.get("rarity", "Unknown")}{prefix} {name.capitalize()}{suffix}",
                    "name": name,
                    "base_experience": base_exp,
                    "card_image": card["images"]["large"],
                    "rarity": card.get("rarity", "Unknown"),
                    "subtypes": subtypes,
                    "value": value,
                    "real_market_value": marketValue,
                    "discrepancy_ratio": round(marketValue / value, 2),
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


@app.get("/test-10-cards")
def getTestPack():
    return {
        "cards": [
            {
                "id": str(uuid.uuid4()),
                "card_title": "Rare Cacturne",
                "name": "cacturne",
                "base_experience": 166,
                "card_image": "https://images.pokemontcg.io/ex14/15_hires.png",
                "rarity": "Rare",
                "subtypes": ["Stage 1"],
                "value": 1.3,
                "real_market_value": 1.33,
                "discrepancy_ratio": 1.02,
            },
            {
                "id": str(uuid.uuid4()),
                "card_title": "Uncommon Dragonair",
                "name": "dragonair",
                "base_experience": 147,
                "card_image": "https://images.pokemontcg.io/sm11/149_hires.png",
                "rarity": "Uncommon",
                "subtypes": ["Stage 1"],
                "value": 0.8,
                "real_market_value": 0.23,
                "discrepancy_ratio": 0.29,
            },
            {
                "id": str(uuid.uuid4()),
                "card_title": "Rare Holo EX Kyurem EX",
                "name": "kyurem",
                "base_experience": 297,
                "card_image": "https://images.pokemontcg.io/bw8/95_hires.png",
                "rarity": "Rare Holo EX",
                "subtypes": ["Basic", "EX"],
                "value": 6.4,
                "real_market_value": 4.51,
                "discrepancy_ratio": 0.7,
            },
            {
                "id": str(uuid.uuid4()),
                "card_title": "Rare Rainbow Dedenne GX",
                "name": "dedenne",
                "base_experience": 151,
                "card_image": "https://images.pokemontcg.io/sm10/219_hires.png",
                "rarity": "Rare Rainbow",
                "subtypes": ["Basic", "GX"],
                "value": 25.2,
                "real_market_value": 30.28,
                "discrepancy_ratio": 1.2,
            },
            {
                "id": str(uuid.uuid4()),
                "card_title": "Common Bellsprout",
                "name": "bellsprout",
                "base_experience": 60,
                "card_image": "https://images.pokemontcg.io/sm2/1_hires.png",
                "rarity": "Common",
                "subtypes": ["Basic"],
                "value": 0.5,
                "real_market_value": 0.13,
                "discrepancy_ratio": 0.26,
            },
            {
                "id": str(uuid.uuid4()),
                "card_title": "Common Quaxly",
                "name": "quaxly",
                "base_experience": 62,
                "card_image": "https://images.pokemontcg.io/sv8/50_hires.png",
                "rarity": "Common",
                "subtypes": ["Basic"],
                "value": 0.5,
                "real_market_value": 0.05,
                "discrepancy_ratio": 0.1,
            },
            {
                "id": str(uuid.uuid4()),
                "card_title": "Illustration Rare Gothita",
                "name": "gothita",
                "base_experience": 58,
                "card_image": "https://images.pokemontcg.io/rsv10pt5/124_hires.png",
                "rarity": "Illustration Rare",
                "subtypes": ["Basic"],
                "value": 6.93,
                "real_market_value": 12.16,
                "discrepancy_ratio": 1.75,
            },
            {
                "id": str(uuid.uuid4()),
                "card_title": "Unknown Munna",
                "name": "munna",
                "base_experience": 58,
                "card_image": "https://images.pokemontcg.io/mcd11/7_hires.png",
                "rarity": "Unknown",
                "subtypes": ["Basic"],
                "value": 0.39,
                "real_market_value": 3.35,
                "discrepancy_ratio": 8.59,
            },
            {
                "id": str(uuid.uuid4()),
                "card_title": "Common Toedscool",
                "name": "toedscool",
                "base_experience": 67,
                "card_image": "https://images.pokemontcg.io/sv9/88_hires.png",
                "rarity": "Common",
                "subtypes": ["Basic"],
                "value": 0.5,
                "real_market_value": 0.15,
                "discrepancy_ratio": 0.3,
            },
            {
                "id": str(uuid.uuid4()),
                "card_title": "Common Trubbish",
                "name": "trubbish",
                "base_experience": 66,
                "card_image": "https://images.pokemontcg.io/sm2/50_hires.png",
                "rarity": "Common",
                "subtypes": ["Basic"],
                "value": 0.5,
                "real_market_value": 0.21,
                "discrepancy_ratio": 0.42,
            },
        ],
        "total_value": 43.02,
        "realworld_total_value": 52.4,
    }


@app.get("/get-set/{set_id}")
def get10Set(set_id: str):
    cards = service.open_pack(set_id)
    if setCount[set_id] > 0:
        setCount[set_id] -= 1
    else:
        return {
            "cards": [
                {
                    "id": str(uuid.uuid4()),
                    "card_title": "GET BLASTED",
                    "name": "YEET YAW",
                    "base_experience": 66,
                    "card_image": "https://tenor.com/jSeIZvj1ZV3.gif",
                    "rarity": "Common",
                    "subtypes": ["Basic"],
                    "value": 0.00,
                    "real_market_value": 0.00,
                    "discrepancy_ratio": 0.00,
                }
            ],
            "total_value": 0.00,
            "realworld_total_value": 0.00,
        }
    return cards


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
