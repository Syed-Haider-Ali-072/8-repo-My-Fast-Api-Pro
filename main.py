from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = FastAPI()

# Static files (like CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# MongoDB connection
client = MongoClient(
    "mongodb://syedhaidersahil:HaiderAli1234.MongoDb@"
    "ac-fwyl2zq-shard-00-00.nnukxa6.mongodb.net:27017,"
    "ac-fwyl2zq-shard-00-01.nnukxa6.mongodb.net:27017,"
    "ac-fwyl2zq-shard-00-02.nnukxa6.mongodb.net:27017/note"
    "?replicaSet=atlas-zfkm5p-shard-0&ssl=true&authSource=admin"
)
db = client["note"]
collection = db["Notes"]

# Store startup time (memory)
startup_time = datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p")

# Home: Show notes
@app.get("/", response_class=HTMLResponse)
async def get_notes(request: Request, q: str = ""):
    query = {"$or": [
        {"title": {"$regex": q, "$options": "i"}},
        {"note": {"$regex": q, "$options": "i"}}
    ]} if q else {}
    notes = list(collection.find(query))
    results = [{"id": str(n["_id"]), "title": n.get("title"), "note": n.get("note")} for n in notes]
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "newDocs": results, "query": q, "startup_time": startup_time}
    )

# Add note
@app.post("/", response_class=HTMLResponse)
async def post_note(request: Request, title: str = Form(...), note: str = Form(...)):
    new_note = {"title": title, "note": note}
    result = collection.insert_one(new_note)
    print(f"New note inserted with ID: {result.inserted_id}")
    return RedirectResponse(url="/", status_code=303)

# Delete note
@app.post("/delete/{note_id}", response_class=HTMLResponse)
async def delete_note(note_id: str):
    result = collection.delete_one({"_id": ObjectId(note_id)})
    print(f"Deleted note with ID: {note_id}")
    return RedirectResponse(url="/", status_code=303)
