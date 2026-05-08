from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List


# ---------- Lots ----------

class CreateLotRequest(BaseModel):
    name: str
    location: str


# ---------- Users ----------

class RegisterRequest(BaseModel):
    username: str
    password: str
    recovery_email: str
    lot_id: int

class LoginRequest(BaseModel):
    username: str
    password: str

# ---------- Slots ----------

class SlotStatus(BaseModel):
    id: int
    slot_number: str
    status: str
    updated_at: datetime
    class Config:
        from_attributes = True

class LotStatusResponse(BaseModel):
    lot_id: int
    lot_name: str
    total_slots: int
    free: int
    occupied: int
    slots: List[SlotStatus]

class SlotsUpdateRequest(BaseModel):
    lot_id: int
    image_key: str = ""
    slots: Dict[str, str]  # { "A1": "empty"/"occupied", "B2": "empty"/"occupied", ... }

class HistoryItem(BaseModel):
    slot_id: int
    slot_number: str
    status: str
    detected_at: datetime
    image_key: str
    class Config:
        from_attributes = True