from sqlalchemy.orm import Session
from sqlalchemy  import select
import model, schemas

def create_user(db:Session, user: schemas.UserCreate):
    new_user = model.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user(db:Session):
    users = db.execute(select(model.User)).scalars().all()
    return db.scalars(all_users).all() #Query = scalars

def update_user(db:Session, user_id:int, user_update: schemas.UpdateUser):
   user = db.scalars(select(model.User).where(model.User.id == user_id)).first()
   if user:
        for key, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user
   return None

def delete_user(db:Session, user_id:int):
    user = db.scalars(select(model.User).where(model.User.id == user_id)).first()
    if user:
        db.delete(user)
        db.commit()
        return {"message": f"User with id {user_id} has been deleted successfully."}
    return None