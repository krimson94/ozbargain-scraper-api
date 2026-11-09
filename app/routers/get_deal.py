from fastapi import APIRouter, HTTPException
from app.services.scraper import fetch_deal
from app.schemas.models import DealResponse

router = APIRouter(prefix="/deal", tags=["Deals"])

@router.get("/{node_id}", response_model=DealResponse)
def get_deal(node_id: int):
    data, status_code = fetch_deal(node_id)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail="Deal not found or blocked by Ozbargain.")
    return data