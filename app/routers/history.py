from fastapi import APIRouter, Depends, HTTPException
from app.database import get_connection
from app.auth import get_current_user

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/{lot_id}")
def get_history(lot_id: int, limit: int = 50, current_user: dict = Depends(get_current_user)):
    """Return the latest detection events for a parking lot (most recent first)."""
    if current_user.get("lot_id") != lot_id:
        raise HTTPException(status_code=403, detail="Access denied: not your lot")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT h.id, h.slot_id, s.slot_number, h.status, h.detected_at, h.image_key
                FROM slot_history h
                JOIN parking_slots s ON h.slot_id = s.id
                WHERE s.lot_id = %s
                ORDER BY h.detected_at DESC
                LIMIT %s
            """, (lot_id, limit))
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()