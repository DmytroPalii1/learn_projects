from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Produkt
from storage import lade_daten, speichere_daten
from typing import Optional

app=FastAPI(
    title="Produkt Management API",
    description="Ein sauberes Backend-System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



@app.get("/")
def home():
    return {"message":"Willkommen zu meiner API!"}


@app.get("/shop")
def alle_produkte(kategorie: Optional[str]=None, max_preis: Optional[float]=None):
    produkte=lade_daten()
    gefilterte_produkte={}
    for p_id, details in produkte.items():
        if kategorie and details["kategorie"].lower() != kategorie.lower():
            continue
        if max_preis and details["preis"]>max_preis:
            continue
        gefilterte_produkte[p_id]=details
    if not gefilterte_produkte:
         return "meldung: Keine passende Produkte gefunden"
    return gefilterte_produkte

    
@app.post("/shop", status_code=201)
def neues_produkt_erstellen(neues_produkt: Produkt):
    produkte_db=lade_daten()

    bestehende_ids=produkte_db.keys()
    neues_id = str(max([int (id) for id in bestehende_ids])+1 if bestehende_ids else 1)
    produkte_db[neues_id]=neues_produkt.model_dump()
    speichere_daten(produkte_db)
    return {
        "meldung": "Produkt erfolgreich hinzugefügt",
        "id": neues_id,
        "produkt": produkte_db[neues_id],
    }

    
@app.get("/shop/{produkt_id}")
def zeige_produkt(produkt_id: int):
    produkte_db=lade_daten()

    if produkt_id in produkte_db:
        return produkte_db[produkt_id]
    raise HTTPException(
        status_code=404, detail="Dieses Produkt existiert nicht!"
    )


@app.put("/shop/{produkt_id}")
def produkt_aktualisieren(produkt_id: str, neues_produkt: Produkt):
    daten=lade_daten()

    if produkt_id not in daten:
        raise HTTPException(
            status_code=404, detail="Produkt nicht gefunden"
        )

    aktualisiertes_produkt = neues_produkt.model_dump()

    daten[produkt_id] = aktualisiertes_produkt
    speichere_daten(daten)

    antwort = aktualisiertes_produkt.copy()
    antwort["id"] = produkt_id
    return antwort


@app.delete("/shop")
def produkt_löschen(produkt_id):
    produkte_db=lade_daten()

    if produkt_id not in produkte_db:
        raise HTTPException(
            status_code=404, detail="Dieses Produkt existiert nicht",
        )
    gelöschtes_produkt=produkte_db.pop(produkt_id)
    speichere_daten(produkte_db)
    return{
        "meldung": f"Produkt mit ID {produkt_id} wurde erfolgreich gelöscht!",
        "gelöschtes Produkt": gelöschtes_produkt,
    }
