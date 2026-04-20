from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

app = FastAPI()

@app.get("/")
def check_status():
    return {"status": "TrustID System Online"}

@app.post("/add-user")
def add_user(name: str, email: str, dob: str, db: Session = Depends(get_db)):
    # This is the SQL command to insert data
    query = text("INSERT INTO users (name, email, dob) VALUES (:n, :e, :d)")
    
    db.execute(query, {"n": name, "e": email, "d": dob})
    db.commit() # This "saves" the changes permanently
    
    return {"message": f"Successfully added {name} to TrustID"}