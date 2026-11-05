from fastapi import APIRouter, HTTPException
from app.services.scraper import fetch_new_deals

router = APIRouter(prefix="",tags=["Deals"])

@router.get("/new")
def new_deals():
    data, status_code = fetch_new_deals()
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail="Deal not found or blocked by Ozbargain.")
    return data