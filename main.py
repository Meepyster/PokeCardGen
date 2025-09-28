import requests
import asyncio
import json
import sqlite3
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
import threading

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


DB_FILE = "set_counts.db"


def get_set(set_id: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT count, regen_per_minute FROM sets WHERE set_id = ?", (set_id,))
    row = c.fetchone()
    conn.close()
    return row


def update_set(set_id: str, new_count: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE sets SET count = ? WHERE set_id = ?", (new_count, set_id))
    conn.commit()
    conn.close()


async def auto_regen():
    while True:
        await asyncio.sleep(60)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT set_id, count, regen_per_minute FROM sets")
        rows = c.fetchall()
        for set_id, count, regen in rows:
            new_count = count + regen
            c.execute("UPDATE sets SET count = ? WHERE set_id = ?", (new_count, set_id))
        conn.commit()
        conn.close()
        print("✅ Regenerated counts for all sets")


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_regen())


@app.get("/get-set/{set_id}")
async def pull(set_id: str):
    row = get_set(set_id)
    if not row:
        return {"error": "Unknown set"}
    count, _ = row
    if count <= 0:
        return {
            "cards": [
                {
                    "id": str(uuid.uuid4()),
                    "card_title": "GET BLASTED",
                    "name": "YEET YAW",
                    "base_experience": 66,
                    "card_image": "https://i.redd.it/2wttjntmyfhd1.png",
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
    update_set(set_id, count - 1)
    return service.open_pack(set_id)


# @app.get("/get-set/{set_id}")
# def get10Set(set_id: str):
#     cards = service.open_pack(set_id)
# if setCount[set_id] > 0:
#     setCount[set_id] -= 1
# else:
#     return {
#         "cards": [
#             {
#                 "id": str(uuid.uuid4()),
#                 "card_title": "GET BLASTED",
#                 "name": "YEET YAW",
#                 "base_experience": 66,
#                 "card_image": "https://i.redd.it/2wttjntmyfhd1.png",
#                 "rarity": "Common",
#                 "subtypes": ["Basic"],
#                 "value": 0.00,
#                 "real_market_value": 0.00,
#                 "discrepancy_ratio": 0.00,
#             }
#         ],
#         "total_value": 0.00,
#         "realworld_total_value": 0.00,
#     }
# return cards


@app.get("/status/{set_id}")
async def status(set_id: str):
    row = get_set(set_id)
    if not row:
        return {"error": "Unknown set"}
    count, regen = row
    return {"set_id": set_id, "remaining": count, "regen_per_minute": regen}


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
