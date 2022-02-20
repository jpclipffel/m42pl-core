from typing import Optional

import asyncio

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import m42pl
from m42pl.event import Event


class PipelineRequest(BaseModel):
    script: str
    event: dict = {}


app = FastAPI()


m42pl.load_modules()


dispatcher = m42pl.dispatcher('local_detached')()


kvstore = m42pl.kvstore('redis')()


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.post('/run')
def run(pipeline: PipelineRequest):
    """Starts as new pipeline.
    """
    try:
        # ---
        pid = dispatcher(
            source=pipeline.script,
            kvstore=kvstore,
            event=Event(pipeline.event)
        )
        # ---
        return {'pid': pid}
    except Exception as error:
        raise HTTPException(400, str(error))
        return {'error': str(error)}
        raise error

@app.get('/status/<pid>')
def status(pid: int):
    """Returns a pipeline status.
    """
    return {'status': asyncio.run(dispatcher.status_str(pid))}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=4242)
