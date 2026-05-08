from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.auth import hash_password, verify_password, create_token
from app.schemas import RegisterRequest, LoginRequest

router = APIRouter(prefix="/users", tags=["users"])

# ---------- Register ----------
@router.post("/register", summary="Register a new admin user")
def register(body: RegisterRequest):
    """Create a new admin account linked to a parking lot."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check duplicate username
            cur.execute("SELECT id FROM users WHERE username = %s", (body.username,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Username already exists")

            hashed = hash_password(body.password)
            cur.execute(
                "INSERT INTO users (username, password, recovery_email, lot_id) VALUES (%s, %s, %s, %s)",
                (body.username, hashed, body.recovery_email, body.lot_id)
            )
        conn.commit()
        return {"message": "Registered successfully"}
    finally:
        conn.close()

# ---------- Login ----------
@router.post("/login", summary="Login and obtain JWT token")
def login(body: LoginRequest):
    """Returns a Bearer JWT token. Include it in the `Authorization` header for protected routes."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (body.username,))
            user = cur.fetchone()

        if not user or not verify_password(body.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        token = create_token({"sub": str(user["id"]), "username": user["username"], "lot_id": user["lot_id"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user["id"],
            "username": user["username"],
            "lot_id": user["lot_id"]
        }
    finally:
        conn.close()