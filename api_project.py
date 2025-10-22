from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, EmailStr, Field
from typing import List
import mysql.connector

app = FastAPI()

def get_conn():
    try:
        return mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            database="fast_api"
        )
    except:
        return None

class User(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    message: str
    total_users: int
    data: List[User] = []

    class Config:
        extra = "allow"

def fetch_users(limit: int = None):
    conn = get_conn()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT username, email, password FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    users = [User(**row) for row in rows]
    if limit:
        users = users[:limit]
    return users

@app.post("/users", response_model=UserResponse)
def add_user(user: User):
    try:
        conn = get_conn()
        if not conn:
            raise HTTPException(status_code=500, detail="DB connection failed")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (user.username, user.email, user.password)
        )
        conn.commit()
        cur.close()
        conn.close()
        users = fetch_users()
        return {"message": "User added successfully!", "total_users": len(users), "data": users}
    except Exception as e:
        print("Error:", e)          # <-- Print the actual error
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users", response_model=UserResponse)
def get_users(limit: int = Query(None, ge=1)):
    users = fetch_users(limit)
    return {"message": "Users fetched successfully!", "total_users": len(users), "data": users}

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int = Path(..., ge=1), user: User = ...):  # Required body
    conn = get_conn()
    if not conn:
        raise HTTPException(status_code=500, detail="DB connection failed")
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    cur.execute(
        "UPDATE users SET username=%s, email=%s, password=%s WHERE id=%s",
        (user.username, user.email, user.password, user_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    users = fetch_users()
    return {"message": f"User {user_id} updated successfully!", "total_users": len(users), "data": users}

@app.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: int = Path(..., ge=1)):
    conn = get_conn()
    if not conn:
        raise HTTPException(status_code=500, detail="DB connection failed")
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    users = fetch_users()
    return {"message": f"User {user_id} deleted successfully!", "total_users": len(users), "data": users}