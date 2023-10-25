from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
from models import userModel as userM
from database import SessionLocal, engine, UserBase
from sqlalchemy.orm import Session
from routes import authRoutes as auth_router

app = FastAPI()
app.include_router(auth_router.router)

userM.Base.metadata.create_all(bind=engine)