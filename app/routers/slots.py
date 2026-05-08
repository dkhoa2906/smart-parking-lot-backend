from fastapi import APIRouter, Depends, HTTPException
from app.database import get_connection
from app.schemas import SlotsUpdateRequest
from app.auth import get_current_user

router = APIRouter(prefix="/slots", tags=["slots"])

@router.get("/{lot_id}", summary="Get current slot statuses")
def get_lot_status(lot_id: int, current_user: dict = Depends(get_current_user)):
    """Return live free/occupied status for every slot in the lot."""
    if current_user.get("lot_id") != lot_id:
        raise HTTPException(status_code=403, detail="Access denied: not your lot")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Get lot info
            cur.execute("SELECT * FROM parking_lots WHERE id = %s", (lot_id,))
            lot = cur.fetchone()
            if not lot:
                raise HTTPException(status_code=404, detail="Lot not found")

            # Get all slots of this lot
            cur.execute(
                "SELECT id, slot_number, status, updated_at FROM parking_slots WHERE lot_id = %s",
                (lot_id,)
            )
            slots = cur.fetchall()

        free = sum(1 for s in slots if s["status"] == "free")
        occupied = sum(1 for s in slots if s["status"] == "occupied")

        return {
            "lot_id": lot["id"],
            "lot_name": lot["name"],
            "total_slots": lot["total_slots"],
            "free": free,
            "occupied": occupied,
            "slots": slots
        }
    finally:
        conn.close()

@router.post("/update", summary="Update slot statuses (called by Lambda)")
def update_slots(payload: SlotsUpdateRequest, current_user: dict = Depends(get_current_user)):
    """
    Called by the Lambda function after Gemini analyzes a parking image.
    Updates the current status of each slot and writes a history record.
    """
    if current_user.get("lot_id") != payload.lot_id:
        raise HTTPException(status_code=403, detail="Access denied: not your lot")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for item in payload.slots:
                # Find slot by lot_id + slot_number
                cur.execute(
                    "SELECT id FROM parking_slots WHERE lot_id = %s AND slot_number = %s",
                    (payload.lot_id, item.slot_number)
                )
                slot = cur.fetchone()
                if not slot:
                    continue

                # Update current status
                cur.execute(
                    "UPDATE parking_slots SET status = %s, updated_at = NOW() WHERE id = %s",
                    (item.status, slot["id"])
                )

                # Write history record
                cur.execute(
                    "INSERT INTO slot_history (slot_id, status, image_key) VALUES (%s, %s, %s)",
                    (slot["id"], item.status, payload.image_key)
                )
        conn.commit()
        return {"message": "Updated successfully", "count": len(payload.slots)}
    finally:
        conn.close()