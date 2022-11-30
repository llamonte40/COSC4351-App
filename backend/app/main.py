from unicodedata import name
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from datetime import date, datetime   


TABLES = ["1A","1B","1C","1D","1E","1F",
"2A","2B","2C","2D","2E","2F",
"3A","3B","3C","3D","3E","3F",
"4A","4B","4C","4D","4E","4F",
"5A","5B","5C","5D","5E","5F"]

class LoginUser(BaseModel):
    email: str
    password: str

class ReservationRequest(BaseModel):
    email: str
    name: str
    phone_no: str
    time : date
    hour : int
    guest: int
    tables: list

client = MongoClient('mongodb+srv://doadmin:5zRc20W74P6rgS39@db-mongodb-sfo3-80898-09a08f1a.mongo.ondigitalocean.com/admin?tls=true&authSource=admin')

db = client["restaurant"]
reservations = db["reservation"]
users = db["loginuser"]

app = FastAPI()

def check_table_availability(time: date,hour: int, guest: int, tables: list) -> bool:
    query_result = reservations.find({"time": datetime.combine(time, datetime.min.time()), "hour": hour},{"_id":0})
    result = []
    for n in query_result:
        print(n)
        result.extend(n["tables"])
    available_tables = list(set(TABLES) - set(result))    

    if not len(available_tables)*2 > guest:
        return "no enough space."
    if len(set(tables)&set(result)) > 0:
        return "selected tables are not available."
    if not len(tables)*2 >= guest:
        return "you have to add more tables to fit."
    
    return  ""

@app.post("/user/login")
def login_user(request: LoginUser):
    query={"email": request.email, "password": request.password}
    query_result = users.count_documents(query)
    if query_result != 1:
        raise HTTPException(status_code=400, detail={
            "message": "Wrong Username or Password."
        })
    return {
        "message": "success"
    }
@app.post("/user/register")
def register_user(request : LoginUser):

    query = {"email": request.email}
    query_result = users.count_documents(query)
    if query_result > 0:
        # Incase that the reservation is found based on the condition above
        raise HTTPException(status_code=400, detail={
            "message": "Email has already registered."
        })
    # Insert new data
    insert_result = users.insert_one({
        "email": request.email,
        "password": request.password,
        "point": 0
    })
    # Return response
    return {
        "message": "success",
        "id": str(insert_result.inserted_id)
    }

@app.get("/user/list")
def get_all_users():
    query_result=users.find({},{"_id": 0})
    result = []
    for n in query_result:
        result.append(n)
    return {
        "result": result
    }

@app.delete("/user/delete")
def remove_user(request : LoginUser):
    query_result=reservations.find({"email": request.email, "password": request.password, "_id": 0})
    result = []
    for n in query_result:
        result.append(n)
    return {
        "result": result
    }

@app.get("/reservation/by-name/{name}")
def get_reservation_by_name(name:str):
    query={"name": name }
    query_result=reservations.find(query, {"_id": 0})
    result = []
    for n in query_result:
        result.append(n)
    return {
        "result": result
    }

@app.get("/reservation/by-date-and-hour/{time}/{hour}")
def get_reservation_by_name(time:date,hour:int):
    query={"time": datetime.combine(time, datetime.min.time()), "hour": hour }
    query_result=reservations.find(query, {"_id": 0})
    result = []
    for n in query_result:
        result.append(n)
    return {
        "result": result
    }

@app.get("/reservation/by-table/{table}")
def get_reservation_by_table(table: int):
    query={"table_number":table}
    query_result=reservations.find(query, {"_id": 0})
    result = []
    for n in query_result:
        result.append(n)
    return {
        "result": result
    }

@app.post("/reservation")
def reserve(reservation : ReservationRequest):
    resp = check_table_availability(reservation.time,reservation.hour, reservation.guest, reservation.tables)
    if len(resp) > 0: 
        # Incase that the reservation is found based on the condition above
        raise HTTPException(status_code=400, detail={
            "message": resp
        })
    
    # Insert new data
    insert_result = reservations.insert_one({
        "email": reservation.email,
        "phone_no": reservation.phone_no,
        "name": reservation.name,
        "time": datetime.combine(reservation.time, datetime.min.time()),
        "hour": reservation.hour,
        "tables": reservation.tables
    })

    #check user is registered, update point
    if users.count_documents({"email":reservation.email}) > 0:
        users.update_one({"email":reservation.email},{"$set":{"point":users.find_one({"email":reservation.email})["point"]+ reservation.guest}}) 


    # Return response
    return {
        "message": "success",
        "id": str(insert_result.inserted_id)
    }

@app.put("/reservation/update/")
def update_reservation(reservation: ReservationRequest):
    query_find = {
        "name": reservation.name
        }
    check = reservations.find(query_find)
    list_check = list(check)
    if len(list_check)==0:
        raise HTTPException(400,f"Couldn't find name:{reservation.name}")

    if not check_table_availability(reservation.time,reservation.table_number):
        raise HTTPException(400,f"Table not available")
    reservations.update_many({"name":reservation.name},{"$set":{"table_number":reservation.table_number,"time":reservation.time}}) 
    return {
        "message": "success"
    }
       
@app.delete("/reservation/delete/{name}/{table_number}")
def cancel_reservation(name: str, table_number : int):
    query = {
        "name":name , 
        "table_number":table_number
         }
    reservations.delete_one(query)
    return {}