#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__Jack__'

import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from tf.main import app_tf
from users.authentication.jwt import app_token
from logconfig import loggers
from users import application

# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import PlainTextResponse
# from starlette.exceptions import HTTPException as StarletteHTTPException


app = FastAPI(
    title='FastAPI Tutorial and Coronavirus Tracker API Docs',
    description='OBLD API接口文档',
    version='1.0.0',
    docs_url='/docs'
)


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    loggers.info(f"process_time: {process_time}")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(application, prefix='/users', tags=['用户注册'])
app.include_router(app_token, prefix='/token', tags=['用户认证'])
app.include_router(app_tf, prefix='/data', tags=['tf模型'])


@app.get('/test')
async def get_test():
    return {'method': 'GET'}


@app.post('/test')
async def get_post_test():
    return {'method': 'POST'}


if __name__ == '__main__':
    uvicorn.run('run:app', host='0.0.0.0', port=8000, reload=True, debug=True, workers=1)
