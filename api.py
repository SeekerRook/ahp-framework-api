import os
import requests
import time
import logging
import numpy as np
from pymcdm.methods import VIKOR

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)
DATA_URL = os.environ["DATA_URL"]
AHP_URL = os.environ["AHP_URL"]

def fetch_data(material = ""):
    start = time.time()
    res = requests.get(DATA_URL+"alternatives/"+material)
    logger.debug(f"datafetch_time {time.time()-start}")
    return res.json()
from fastapi import FastAPI, HTTPException
def ahp(alternatives,preferences):
    start = time.time()
    payload = {}
    payload["alternatives"] = alternatives
    payload["preferences"] = preferences
    res = requests.post(AHP_URL+"mcdm_api/alternatives",json=payload)
    selection =  res.json()       
    #logger.debug(selection) 
    logger.debug(f"ahp_time {time.time()-start}")
    return selection

def run_ahp(alternatives,materials,preferences=[]):
    res = {}
    for i,material in enumerate(materials):
        selection = ahp(alternatives[material],preferences[i])

        try:
            #selection = lternatives[material][ahp(alternatives[material],preferences[i])]
            res[material] = {"MaterialID" : selection["best_alternative"]["materialID"],"supplierID" : selection["best_alternative"]["supplierID"]}
        except:
            return {"RESULT":"ERROR","RESPONSE":selection}

    return res
def run_ahp_full(alternatives,materials,preferences=[]):
    res = {}
    for i,material in enumerate(materials):
        selection = ahp(alternatives[material],preferences[i])


        res[material] = selection#{"MaterialID" : selection["best_alternative"]["materialID"],"supplierID" : selection["best_alternative"]["supplierID"]}


    return res
def vikor(matrix,
        weights,
        types,

        v=0.5):

    body = VIKOR()


    res = body(matrix,weights,types)

    return res
def make_DM(alternatives):
    result = []
    for alt in alternatives:
        r = [alt[f"C{i+1}"] for i in range(7)]
        result.append(r)
    return np.array(result)
def weight_transform(w,kpi_w=[0.55,0.45,1,0.6,0.4,0.5,0.5]):

    return [w[0]*kpi_w[0],w[0]*kpi_w[1],w[1]*kpi_w[2],w[2]*kpi_w[3],w[2]*kpi_w[4],w[3]*kpi_w[5],w[3]*kpi_w[6]]


def run_vikor(alternatives,materials,preferences=[]):
    start = time.time()

    res = {}
    for i,material in enumerate(materials):
        dm = make_DM(alternatives=alternatives[material])
        w = weight_transform(preferences[i])
        selection = vikor(dm,w,types=[1,1,-1,-1,1,1,1])


        res[material] = f"{selection}"#{"MaterialID" : selection["best_alternative"]["materialID"],"supplierID" : selection["best_alternative"]["supplierID"]}

    logger.debug(f"vikor_time {time.time()-start}")

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
        logger.debug(f"Order-Custom")
        start = time.time()
        materials = order.get("materials", [])
        preferences = order.get("preferences")
        data = fetch_data()
           
        selection = run_ahp(data,materials,preferences)
        return selection
        logger.debug(f"Total  {time.time()-start}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/order/simple", summary="Execute order, with preferences as natural language descriptors")

async def manage_order(order: dict = Body(...)):
    try:
        logger.debug(f"Order-Simple")
        start = time.time()
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
        logger.debug(f"Total  {time.time()-start}")
        
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ahp/simple", summary="Execute order, with preferences as natural language descriptors")

async def manage_order(order: dict = Body(...)):
    try:
        logger.debug(f"Order-Simple")
        start = time.time()
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
           
        selection = run_ahp_full(data,materials,preferences)
        logger.debug(f"Total(AHP)  {time.time()-start}")
        
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vikor/simple", summary="Execute order, with preferences as natural language descriptors")

async def manage_order(order: dict = Body(...)):
    try:
        logger.debug(f"Order-Simple")
        start = time.time()
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
           
        selection = run_vikor(data,materials,preferences)
        logger.debug(f"Total(VIKOR)  {time.time()-start}")
        
        return selection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))









@app.get("/health")
def health():
    return {"status": "ok"}