from fastapi import FastAPI
from app.routers import get_deal, new_deals

app = FastAPI(title="Ozbargain Scraper API", description="API for Ozbargain scraping")

app.include_router(get_deal.router)

@app.get("/")
def home():
    return {"status": "running", "docs": "/docs"}