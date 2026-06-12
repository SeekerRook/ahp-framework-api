import os
import requests



DATA_URL = os.environ["DATA_URL"]
# AHP_URL = os.environ["AHP_URL"]

def fetch_data(material = ""):
    res = requests.get(DATA_URL+"alternatives/"+material)
    return res.json()
from fastapi import FastAPI, HTTPException
def ahp(alternatives,intent):
    #TODO : use actual AHP from microservice
    import random
    res = random.choice(alternatives)
    res["intent"] = intent 
    return res
def run_ahp(alternatives,materials,intent={}):
    res = {}
    for material in materials:
        res[material] = ahp(alternatives[material],intent)
    return res
from fastapi import FastAPI, HTTPException,Body

app = FastAPI(title="Materials API")
@app.get("/data", summary="Get all material alternatives with supplier scores")
def get_alternatives():
    try:
        return fetch_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/{material_type}", summary="Get alternatives for a specific material type")
def get_alternatives_by_type(material_type: str):

    try:
        return fetch_data(material_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/select_supplier/{material_type}", summary="Get alternatives for a specific material type")
def get_supplier_by_type(material_type: str):
    try:
        data = fetch_data(material_type)
        selection = run_ahp(data,[material_type])
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/select_supplier", summary="Get alternatives for a specific material type")
def get_supplier_by_type():
    try:
        data = fetch_data()
        selection = run_ahp(data,list(data.keys()))
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/select_supplier/{material_type}", summary="Get alternatives for a specific material type")
def get_supplier_by_type(material_type: str):
    try:
        data = fetch_data(material_type)
        selection = run_ahp(data)
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/order", summary="Get alternatives for a specific material type")

async def manage_order(order: dict = Body(...)):
    try:
        materials = order.get("materials", [])
        intent = order.get("intent")
        data = fetch_data()
           
        selection = run_ahp(data,materials,intent)
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







@app.get("/health")
def health():
    return {"status": "ok"}