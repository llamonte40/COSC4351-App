from unicodedata import name
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

class Reservation(BaseModel):
    name : str
    time: int
    table_number: int
    
client = MongoClient('mongodb+srv://doadmin:5zRc20W74P6rgS39@db-mongodb-sfo3-80898-09a08f1a.mongo.ondigitalocean.com/admin?tls=true&authSource=admin')

db = client["restaurant"]
collection = db["reservation"]

app = FastAPI()

def check_table_availability(time: int, table: int) -> bool:
    result = collection.find({"time": time, "table_number": table})
    list_cursor = list(result)
    return not len(list_cursor) > 0

@app.get("/reservation/by-name/{name}")
def get_reservation_by_name(name:str):
    query={"name": name }
    query_result=collection.find(query, {"_id": 0})
    result = []
    for n in query_result:
        result.append(n)
    return {
        "result": result
    }

@app.get("/reservation/by-table/{table}")
def get_reservation_by_table(table: int):
    query={"table_number":table}
    query_result=collection.find(query, {"_id": 0})
    result = []
    for n in query_result:
        result.append(n)
    return {
        "result": result
    }


@app.post("/reservation")
def reserve(reservation : Reservation):

    if not check_table_availability(reservation.time, reservation.table_number):
        # Incase that the reservation is found based on the condition above
        raise HTTPException(status_code=400, detail={
            "message": "That table isn't available at that time"
        })
    # Insert new data
    insert_result = collection.insert_one({
        "name": reservation.name,
        "time": reservation.time,
        "table_number": reservation.table_number
    })
    # Return response
    return {
        "message": "success",
        "id": str(insert_result.inserted_id)
    }

@app.put("/reservation/update/")
def update_reservation(reservation: Reservation):
    query_find = {
        "name": reservation.name
        }
    check = collection.find(query_find)
    list_check = list(check)
    if len(list_check)==0:
        raise HTTPException(400,f"Couldn't find name:{reservation.name}")

    if not check_table_availability(reservation.time,reservation.table_number):
        raise HTTPException(400,f"Table not available")
    collection.update_many({"name":reservation.name},{"$set":{"table_number":reservation.table_number,"time":reservation.time}}) 
    return {
        "message": "success"
    }
    
        
@app.delete("/reservation/delete/{name}/{table_number}")
def cancel_reservation(name: str, table_number : int):
    query = {
        "name":name , 
        "table_number":table_number
         }
    collection.delete_one(query)
    return {}