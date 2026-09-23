from pydantic import BaseModel, Field

class Produkt(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="Name des Produkts")
    preis: float = Field(gt=0, description="Preis muss groesser als 0 sein")
    kategorie: str = Field(min_length=2, max_length=50, description="Kategorie des Produkts", default="Allgemein")
