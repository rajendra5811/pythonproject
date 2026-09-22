from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, model, schemas
from database import get_db, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/users/", response_model=schemas.UserRead)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.get("/users", response_model=list[schemas.UserRead])
def get_users(db: Session = Depends(get_db)):
    return crud.get_user(db=db)

@app.put("/users/{user_id}", response_model = schemas.UserRead)
def update_user(user_id: int, user_update: schemas.UpdateUser, db: Session = Depends(get_db)):
    user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}", response_model = dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.delete_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user