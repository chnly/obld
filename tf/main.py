import requests
from fastapi import APIRouter

app_tf = APIRouter()


@app_tf.post("/")
async def get_car_info():
    pass
