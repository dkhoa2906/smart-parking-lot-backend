from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.schemas import CreateLotRequest

router = APIRouter(prefix="/lots", tags=["lots"])


@router.post("", status_code=201, summary="Create a new parking lot")
def create_lot(body: CreateLotRequest):
    """Create a new parking lot. Returns the created lot with its assigned ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO parking_lots (name, location) VALUES (%s, %s)",
                (body.name, body.location),
            )
            lot_id = cur.lastrowid
        conn.commit()
        return {"lot_id": lot_id, "name": body.name, "location": body.location}
    finally:
        conn.close()
