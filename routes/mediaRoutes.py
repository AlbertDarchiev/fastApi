import copy
from fastapi import FastAPI, HTTPException, Depends, APIRouter, File, Form, UploadFile
from database import SessionLocal, engine, UserBase, RouteBase, LocationBase, ImageBase, LocationCommentBase
import models 
from typing import List, Annotated, Union
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, select
from models import routeModel as routeM
from models import userModel, locationModel, imageModel, coutryModel, routeLikesModel, routeModel, locationCommnetModel
from datetime import datetime
import base64
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close() 
db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/country/")
def get_country_route(db: db_dependency):
    country_info = db.query(coutryModel.Country).all()
    if not country_info:
        raise HTTPException(status_code=404, detail="Country not found")
    return country_info

# SAVE LOCATION --------------------------------------------------------------------
@router.patch("/save/location/")
def save_location(db: db_dependency, user_id : int, location_id: int):
    location = db.query(locationModel.Location).filter(locationModel.Location.id == location_id).first()
    user = db.query(userModel.Users).filter(userModel.Users.id == user_id).first()
    saved_loc = user.saved_locations

    if not location:
        raise HTTPException(status_code=404, detail="Location id not found")
    elif not user:
        raise HTTPException(status_code=404, detail="User id not found")
    elif location_id in saved_loc:
        raise HTTPException(status_code=404, detail="Location already saved")
    else :
        new_data = copy.copy(user.saved_locations)
        new_data.append(location_id)
        user.saved_locations = new_data
        db.commit()
        db.refresh(user)
        return user
    
# SAVE ROUTE --------------------------------------------------------------------
@router.patch("/save/route/")
def save_location(db: db_dependency, user_id : int, route_id: int):
    route = db.query(routeModel.Route).filter(routeModel.Route.id == route_id).first()
    user = db.query(userModel.Users).filter(userModel.Users.id == user_id).first()
    saved_route = user.saved_routes

    if not route:
        raise HTTPException(status_code=404, detail="Route id not found")
    elif not user:
        raise HTTPException(status_code=404, detail="User id not found")
    elif route_id in saved_route:
        raise HTTPException(status_code=404, detail="Route already saved")
    else :
        new_data = copy.copy(user.saved_routes)
        new_data.append(route_id)
        user.saved_routes = new_data
        db.commit()
        db.refresh(user)
        return user
    
# UNSAVE LOCATION --------------------------------------------------------------------
@router.patch("/unsave/location/")
def save_location(db: db_dependency, user_id : int, location_id: int):
    location = db.query(locationModel.Location).filter(locationModel.Location.id == location_id).first()
    user = db.query(userModel.Users).filter(userModel.Users.id == user_id).first()
    saved_loc = user.saved_locations

    if not location:
        raise HTTPException(status_code=404, detail="Location id not found")
    elif not user:
        raise HTTPException(status_code=404, detail="User id not found")
    elif location_id not in saved_loc:
        raise HTTPException(status_code=404, detail="Location already unsaved")
    else :
        new_data = copy.copy(user.saved_locations)
        new_data.remove(location_id)
        user.saved_locations = new_data
        db.commit()
        db.refresh(user)
        return user

# UNSAVE ROUTE --------------------------------------------------------------------
@router.patch("/unsave/route/")
def unsave_route(db: db_dependency, user_id : int, route_id: int):
    route = db.query(routeModel.Route).filter(routeModel.Route.id == route_id).first()
    user = db.query(userModel.Users).filter(userModel.Users.id == user_id).first()
    saved_route = user.saved_routes

    if not route:
        raise HTTPException(status_code=404, detail="Route id not found")
    elif not user:
        raise HTTPException(status_code=404, detail="User id not found")
    elif route_id not in saved_route:
        raise HTTPException(status_code=404, detail="Route already unsaved")
    else :
        new_data = copy.copy(user.saved_routes)
        new_data.remove(route_id)
        user.saved_routes = new_data
        db.commit()
        db.refresh(user)
        return user

# ROUTE ROUTES ---------------------------------------------------------------------
@router.get("/route/more_likes/")
def get_media_more_likes_route(db: db_dependency):
    route_info = db.query(routeModel.Route).join(routeLikesModel.RouteLikes).group_by(routeModel.Route.id).order_by(func.count(routeLikesModel.RouteLikes.route_id).desc()).all()
    responses = []
    if not route_info:
        raise HTTPException(status_code=404, detail="Route not found")
    for route in route_info:
        print(route.location_id)
        locations = []
        for i, loc in enumerate(route.location_id):
            location = db.query(locationModel.Location).filter(locationModel.Location.id == route.location_id[i]).first()
            image = db.query(imageModel.Image).filter(imageModel.Image.id == location.image_id).first()
            location.image = image.image_uri
            locations.append(location)
        route.location_id = locations
        responses.append(route)
    return responses

@router.get("/route")    
def get_media_route(db: db_dependency):
    route_info = db.query(routeModel.Route).all()
    responses = []
    if not route_info:
        raise HTTPException(status_code=404, detail="Route not found")
    for route in route_info:
        locations = []
        for i, loc in enumerate(route.location_id):
            location = db.query(locationModel.Location).filter(locationModel.Location.id == route.location_id[i]).first()
            image = db.query(imageModel.Image).filter(imageModel.Image.id == location.image_id).first()
            location.image = image.image_uri
            locations.append(location)
        route.location_id = locations
        responses.append(route)
    return responses

@router.get("/route/{country_name}")
def get_route_by_country_route(country_name: str, db: db_dependency):
    country = db.query(coutryModel.Country).filter(coutryModel.Country.name == country_name).first()
    if country is None:
        raise HTTPException(status_code=404, detail="Country not foundd")
    
    route_info = db.query(routeM.Route).filter(routeModel.Route.country_id == country.id).all()
    responses = []
    for route in route_info:
        locations = []
        for i, loc in enumerate(route.location_id):
            location = db.query(locationModel.Location).filter(locationModel.Location.id == route.location_id[i]).first()
            image = db.query(imageModel.Image).filter(imageModel.Image.id == location.image_id).first()
            location.image = image.image_uri
            locations.append(location)
        route.location_id = locations
        responses.append(route)
    return route_info

@router.post("/create_route/{country_name}", response_model=RouteBase)
def create_route_route(country_name: str, route: RouteBase, db: db_dependency):
    country_name = db.query(coutryModel.Country).filter(coutryModel.Country.name == country_name).first().id
    db_route = routeM.Route(
        name=route.name,
        description=route.description,
        distance=route.distance,
        duration=route.duration,
        country_id=country_name,
        location_id=route.location_id
        )
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route

@router.post("/save_route", response_model=RouteBase)
def save_route(db:db_dependency, country_name:str, route: RouteBase = Depends()):
    db_route = routeModel.Route(
        name = route.name,
        descirption = route.description,
        distance = route.distance,
        duration = route.duration,
        country_id = db.query(coutryModel.Country).filter(coutryModel.Country.name == country_name).first().id,
        location_id = route.location_id
    )
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route


# LOCATION ROUTES ---------------------------------------------------------------------

@router.get("/location")
def get_location(db: db_dependency): 
    location_info = db.query(locationModel.Location).all()
    responses = []
    if not location_info:
        raise HTTPException(status_code=404, detail="Location not found")
    
    for loc in location_info:
        db_image = db.query(imageModel.Image.image_uri).filter(imageModel.Image.id == loc.image_id).first()
        if db_image is not None:
            loc.image = db_image[0]
        else:
            loc.image = []
        responses.append(loc)
    return responses

@router.get("/location/{country_name}")
def get_location_route(country_name:str, db: db_dependency):
    country = db.query(coutryModel.Country).filter(coutryModel.Country.name == country_name).first()
    if country is None:
        raise HTTPException(status_code=404, detail="Country not foundasdasdsad")

    location_info = db.query(locationModel.Location).filter(locationModel.Location.country_id == country.id).all()
    responses = []
    if not location_info:
        raise HTTPException(status_code=404, detail="Location not found")

    for loc in location_info:
        db_image = db.query(imageModel.Image.image_uri).filter(imageModel.Image.id == loc.image_id).first()
        if db_image is not None:
            loc.image = db_image[0]
        else:
            loc.image = []
        responses.append(loc)
    return responses

@router.get("/location/id/{loc_id}")
def get_location_by_id(loc_id:int, db: db_dependency):
    location_info = db.query(locationModel.Location).filter(locationModel.Location.id == loc_id).first()
    
    responses = []
    if location_info is None:
        raise HTTPException(status_code=404, detail="Location not found")
    else:
        image = db.query(imageModel.Image).filter(imageModel.Image.id == location_info.image_id).first().image_uri
        if image is not None:
            location_info.image = image
        else:
            location_info.image = []
        responses.append(location_info)
    return responses

@router.post("/create_location/{country_name}", response_model=LocationBase)
async def create_location_location( country_name: str, db: db_dependency, image_files: List[str], location: LocationBase):
    
    loc_date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db_location = locationModel.Location(
        name = location.name,
        description = location.description,
        creation_date=loc_date,
        country_id=db.query(coutryModel.Country).filter(coutryModel.Country.name == country_name).first().id,
        longitude = location.longitude,
        latitude = location.latitude
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    
    list_images_name = []
    # https://ik.imagekit.io/albertITB/locationImg/$[datetime.now()]
    for i, image in enumerate(image_files):
        date = str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S"))
        #img_ext = image.filename.split(".")[1]
        list_images_name.append(f"https://ik.imagekit.io/albertITB/locationImg/{date}.png")
        image_name = f"{date}.png"
        await upload_file("locationImg" ,image_name , image)

    loc_id = db.query(locationModel.Location).filter(locationModel.Location.creation_date == loc_date).first().id
    db_image = imageModel.Image(
        location_id=loc_id,
        image_uri=list_images_name
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    db.query(locationModel.Location).filter_by(creation_date=loc_date).update(
        {
        locationModel.Location.image_id: db_image.id,
        })
    
    db.commit()
    db.refresh(db_location)
    return JSONResponse( status_code=201, content="Location created successfully")

#DONT WORK
@router.post("/add_comment", response_model=LocationCommentBase)
async def create_location_location( db: db_dependency, comment: LocationCommentBase):
    date_now = datetime.now()
    loc_id_exists = db.query(locationModel.Location).filter(locationModel.Location.id == comment.location_id).first()
    if not loc_id_exists:
        raise HTTPException(status_code=404, detail="Location id not found")

    db_comment = locationCommnetModel.Location_comment(
        user_id = comment.user_id,
        location_id = comment.location_id,
        comment = comment.comment,
        date = date_now
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    db.close()
    return JSONResponse( status_code=201, content="Comment posted successfully")

async def upload_file(foldername: str, image_name:str, file: base64):
    imagekit = ImageKit(
        private_key='private_iDHFe+AfM2FSVeBe1o11jqllHB4=',
        public_key='public_SWebOtYLMFIFinKilKGXkwGFAoM=',
        url_endpoint='https://ik.imagekit.io/albertITB'
    )
    #content = await file
    #image_base64 = base64.b64encode(content).decode("utf-8")

    imagekit.upload(
        file, #se especifica el archivo a subir
        file_name=image_name, #se especifica el nombre del archivo
        options=UploadFileRequestOptions( #se especifican las opciones de subida(con las que hay ahora tenemos suficiente)
            use_unique_file_name=False,
            folder=foldername
        ))