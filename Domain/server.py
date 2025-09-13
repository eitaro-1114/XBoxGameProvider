from threading import Thread

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Server is Online."}


def _start():
    uvicorn.run(app, host="0.0.0.0", port=8080)


def server_thread():
    """Koyeb で動かすためのサーバースレッド"""
    t = Thread(target=_start)
    t.start()
