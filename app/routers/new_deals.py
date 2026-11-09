from fastapi import APIRouter, HTTPException
from app.services.scraper import fetch_new_deals
from app.schemas.models import NewDealResponse

router = APIRouter(prefix="",tags=["Deals"])

@router.get("/new", response_model=list[NewDealResponse])
def new_deals():
    data, status_code = fetch_new_deals()
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail="Deal not found or blocked by Ozbargain.")
    return data