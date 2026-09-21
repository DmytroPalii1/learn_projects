import json
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app=FastAPI()


class Produkt(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="Name des Produkts")
    preis: float = Field(gt=0, description="Preis muss groesser als 0 sein")
    kategorie: str = Field(min_length=2, max_length=50, description="Kategorie des Produkts", default="Allgemein")


def lade_daten():
    with open("produkte.json","r",encoding="utf-8") as f:
        return json.load(f)


def speichere_daten(daten):
    with open("produkte.json","w",encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=4)


@app.get("/")
def home():
    return {"message":"Willkommen zu meiner API!"}


@app.get("/shop")
def alle_produkte(kategorie: Optional[str]=None, max_preis: Optional[float]=None):
    produkte_db=lade_daten()
    gefilterte_produkte={}
    for p_id, details in produkte_db.items():
        if kategorie and details["kategorie"].lower() != kategorie.lower():
            continue
        if max_preis and details["preis"]>max_preis:
            continue
        gefilterte_produkte[p_id]=details
    if not gefilterte_produkte:
         return "meldung: Keine passende Produkte gefunden"
    return gefilterte_produkte

    
@app.post("/shop")
def neues_produkt_erstellen(neues_produkt: Produkt):
    produkte_db=lade_daten()

    bestehende_ids = [int(i) for i in produkte_db.keys()]
    neues_id = str(max(bestehende_ids)+1 if bestehende_ids else 1)
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
