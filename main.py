import logging
from typing import Optional

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from iata.bcbp import decode, encode
from iata.bcbp.models import BarcodedBoardingPass
from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

app = FastAPI(title="IATA BCBP", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
router = APIRouter(prefix="/iata/api")


class DecodeRequest(BaseModel):
    barcode: str = Field(min_length=1, max_length=1000)
    year: Optional[int] = Field(None, ge=1800, le=2400)


class BarcodeResponse(BaseModel):
    barcode: str


@router.post("/decode", response_model=BarcodedBoardingPass)
def decode_barcode(req: DecodeRequest):
    try:
        return decode(req.barcode, req.year)
    except Exception:
        log.exception("decode failed")
        raise HTTPException(status_code=400, detail="Invalid barcode")


@router.post("/encode", response_model=BarcodeResponse)
def encode_barcode(bcbp: BarcodedBoardingPass):
    legs = bcbp.data.legs if bcbp.data else []
    if not legs:
        raise HTTPException(
            status_code=422, detail="Ensure at least one flight leg is provided"
        )
    if len(legs) > 9:
        raise HTTPException(
            status_code=422, detail="A boarding pass may contain at most 9 legs"
        )
    try:
        result = encode(bcbp)
    except Exception:
        log.exception("encode failed")
        raise HTTPException(status_code=400, detail="Encoding failed")
    if not result:
        raise HTTPException(
            status_code=422, detail="Ensure at least one flight leg is provided"
        )
    return BarcodeResponse(barcode=result)


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, server_header=False, date_header=False
    )
