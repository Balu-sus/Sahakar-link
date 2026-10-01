from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from auth import hash_password, verify_password, create_access_token, decode_access_token, get_db_connection
import uuid

app = FastAPI(
    title="Sahakar-Link API Gateway",
    description="Central Authentication, Authorization, and Microservices Proxy Gateway",
    version="1.0.0"
)

# Schemas
class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: str = None
    preferred_language: str = "en"
    role: str # STUDENT, TRAINER, ADMIN, EMPLOYER

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# RBAC Middleware Helper
def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token header format")
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    return payload

@app.post("/api/v1/auth/register")
def register_user(req: RegisterUserRequest):
    if req.role not in ['STUDENT', 'TRAINER', 'ADMIN', 'EMPLOYER']:
        raise HTTPException(status_code=400, detail="Invalid role specified")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE email = %s", (req.email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="User email already registered")

    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(req.password)

    cursor.execute("""
        INSERT INTO users (id, email, password_hash, full_name, phone_number, preferred_language, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, req.email, hashed_pwd, req.full_name, req.phone_number, req.preferred_language, req.role))
    
    conn.commit()
    cursor.close()
    conn.close()

    token = create_access_token({"user_id": user_id, "email": req.email, "role": req.role})
    return {"status": "success", "user_id": user_id, "access_token": token, "token_type": "bearer"}

@app.post("/api/v1/auth/login")
def login(req: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, password_hash, role, full_name FROM users WHERE email = %s", (req.email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not verify_password(req.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": str(user['id']), "email": user['email'], "role": user['role']})
    return {
        "status": "success",
        "user_id": str(user['id']),
        "full_name": user['full_name'],
        "role": user['role'],
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/api/v1/users/me")
def get_user_profile(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, phone_number, preferred_language, role, created_at FROM users WHERE id = %s", (current_user['user_id'],))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()

    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"status": "success", "profile": profile}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
