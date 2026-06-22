import os
import requests



DATA_URL = os.environ["DATA_URL"]
AHP_URL = os.environ["AHP_URL"]

def fetch_data(material = ""):
    res = requests.get(DATA_URL+"alternatives/"+material)
    return res.json()
from fastapi import FastAPI, HTTPException
def ahp(alternatives,preferences):
    payload = {}
    payload["alternatives"] = alternatives
    payload["preferences"] = preferences
    res = requests.post(AHP_URL+"mcdm_api/alternatives",json=payload)
    selection =  res.json()       
    #print(selection) 
    try:
        return {"MaterialID" : selection["best_alternative"]["materialID"],"supplierID" : selection["best_alternative"]["supplierID"]}
    except:
        return {"RESULT":"ERROR","PAYLOAD":payload,"RESPONSE":selection}
def run_ahp(alternatives,materials,preferences=[]):
    res = {}
    for i,material in enumerate(materials):
        try:
            #selection = lternatives[material][ahp(alternatives[material],preferences[i])]
            res[material] = ahp(alternatives[material],preferences[i])
        except:
            return ahp(alternatives[material],preferences[i])
    return res
from fastapi import FastAPI, HTTPException,Body

app = FastAPI(title="Framework API")
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


@app.get("/select_supplier", summary="Get supplier selection for all material types")
def get_supplier_by_type():
    try:
        data = fetch_data()
        recommended = [0.35,0.15,0.35,0.15]
        selection = run_ahp(data,list(data.keys()),recommended)
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/select_supplier/{material_type}", summary="Get supplier selection for a specific material type (test only)")
def get_supplier_by_type(material_type: str):
    try:
        data = fetch_data(material_type)
        recommended = [0.35,0.15,0.35,0.15]
        selection = run_ahp(data,[material_type],recommended)
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/order/custom", summary="Execute order, with preferences as numerical weights")

async def manage_order(order: dict = Body(...)):
    try:
        materials = order.get("materials", [])
        preferences = order.get("preferences")
        data = fetch_data()
           
        selection = run_ahp(data,materials,preferences)
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/order/simple", summary="Execute order, with preferences as natural language descriptors")

async def manage_order(order: dict = Body(...)):
    try:
        intent_map = {
            "balanced":[0.25,0.25,0.25,0.25],
            "cost":[0.1,0.1,0.7,0.1],
            "quality":[0.7,0.1,0.1,0.1],
            "delivery":[0.1,0.7,0.1,0.1],
            "environment":[0.1,0.1,0.1,0.7],
            "recommended":[0.35,0.15,0.35,0.15]
        }
        materials = order.get("materials", [])
        preferences = [intent_map[i] for i in order.get("preferences")]
        data = fetch_data()
           
        selection = run_ahp(data,materials,preferences)
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







@app.get("/health")
def health():
    return {"status": "ok"}