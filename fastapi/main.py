from fastapi import FastAPI, HTTPException
from typing import Dict, Optional
import asyncio
import copy
import json
from pydantic import BaseModel

class TransactionRequest(BaseModel):
    transaction_id: str
    commands: list

class Database:
    def __init__(self, filename):
        self.data = {}
        self.temp_data = {}
        self.lock = asyncio.Lock()
        self.filename = filename
        self.active_transactions = {}  # New dictionary for active transactions
        self.transaction_counter = 0  # New variable to track the transaction counter
        try:
            with open(filename, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            pass

    async def start_transaction(self):
            async with self.lock:
                self.transaction_counter += 1  # Increment the transaction counter
                transaction_id = str(self.transaction_counter)
                self.active_transactions[transaction_id] = copy.deepcopy(self.data)
                return {"status": "Ok", "mesg": "Transaction started", "transaction_id": transaction_id}
            
    async def commit(self, transaction_id):
        async with self.lock:
            if transaction_id not in self.active_transactions:
                raise HTTPException(status_code=404, detail="Transaction not found")
            self.data = copy.deepcopy(self.active_transactions[transaction_id])
            with open(self.filename, "w") as f:
                json.dump(self.data, f)
            del self.active_transactions[transaction_id]
            return {"status": "Ok", "mesg": "Transaction committed"}

    async def rollback(self, transaction_id):
        async with self.lock:
            if transaction_id not in self.active_transactions:
                raise HTTPException(status_code=404, detail="Transaction not found")
            del self.active_transactions[transaction_id]
            return {"status": "Ok", "mesg": "Transaction rolled back"}

    async def add_or_update(self, key: str, value: str, transaction_id):
        async with self.lock:
            if transaction_id not in self.active_transactions:
                raise HTTPException(status_code=404, detail="Transaction not found")
            self.active_transactions[transaction_id][key] = value
            return {"status": "Ok", "mesg": "Key-value pair added/updated"}

    async def delete(self, key: str, transaction_id):
        async with self.lock:
            if transaction_id not in self.active_transactions:
                raise HTTPException(status_code=404, detail="Transaction not found")
            if key in self.active_transactions[transaction_id]:
                del self.active_transactions[transaction_id][key]
                return {"status": "Ok", "mesg": "Key-value pair deleted"}
            else:
                raise HTTPException(status_code=404, detail="Key not found")

app = FastAPI()

database = Database("db.json")

@app.post("/start")
async def start_transaction():
    """Endpoint to start a transaction."""
    return await database.start_transaction()

@app.post("/commit/{transaction_id}")
async def commit_transaction(transaction_id: str):
    """Endpoint to commit a transaction."""
    return await database.commit(transaction_id)

@app.post("/rollback/{transaction_id}")
async def rollback_transaction(transaction_id: str):
    """Endpoint to rollback a transaction."""
    return await database.rollback(transaction_id)

@app.put("/set/{transaction_id}/{key}")
async def add_or_update(key: str, value: str, transaction_id: str):
    """Endpoint to add or update a value by key during a transaction."""
    return await database.add_or_update(key, value, transaction_id)

@app.delete("/delete/{transaction_id}/{key}")
async def delete_item(key: str, transaction_id: str):
    """Endpoint to delete a value by key during a transaction."""
    return await database.delete(key, transaction_id)

@app.get("/get/{key}")
async def read_item(key: str):
    """Endpoint to get a value by key."""
    async with database.lock:
        if key in database.data:
            value = database.data.get(key, None)
            if value is not None:
                return {"status": "Ok", "result": value}
            else:
                return {"status": "Error", "mesg": "Key not found"}

@app.post("/execute")
async def execute_commands(request: TransactionRequest):
    """Endpoint to execute transaction control and data modification commands."""
    response = []
    for command in request.commands:
        if command["command"] == "START":
            result = await database.start_transaction()
        elif command["command"] == "COMMIT":
            result = await database.commit(request.transaction_id)
        elif command["command"] == "ROLLBACK":
            result = await database.rollback(request.transaction_id)
        elif command["command"] == "ADD_OR_UPDATE":
            result = await database.add_or_update(command["key"], command["value"], request.transaction_id)
        elif command["command"] == "DELETE":
            result = await database.delete(command["key"], request.transaction_id)
        else:
            result = {"status": "Error", "mesg": "Invalid command"}
        response.append(result)
    return response

@app.get("/view")
async def view_data():
    """Endpoint to view the contents of the in-memory dataset."""
    return database.data
