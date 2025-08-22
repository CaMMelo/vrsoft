import asyncio
import json
from dataclasses import asdict
from uuid import UUID, uuid4

import aio_pika
from fastapi import FastAPI, HTTPException, Request, status

from backend import config, model

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    app.state.notificacoes = dict()
    app.state.rabbitmq_connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
    app.state.rabbitmq_channel = await app.state.rabbitmq_connection.channel()

    from backend import dlq, entrada, retries, validacao

    await app.state.rabbitmq_channel.declare_queue(
        "fila.notificacao.entrada.caiomelo", durable=True
    )

    asyncio.create_task(entrada.main(app.state.notificacoes))
    asyncio.create_task(validacao.main(app.state.notificacoes))
    asyncio.create_task(retries.main(app.state.notificacoes))
    asyncio.create_task(dlq.main(app.state.notificacoes))


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.rabbitmq_connection.close()


@app.post("/api/notificar", status_code=status.HTTP_202_ACCEPTED)
async def __notificar(payload: model.PayloadNotificacao, request: Request):
    channel = request.app.state.rabbitmq_channel
    result = await model.notificar(payload, channel, app.state.notificacoes)
    return {
        "mensagemId": result.mensagemId,
        "traceId": result.traceId,
    }


@app.get("/api/notificacao/status/{traceId}")
def __status(traceId: UUID):
    if f"{traceId}" not in app.state.notificacoes:
        raise HTTPException(status_code=404, detail="notificacao nao encontrada.")
    return asdict(app.state.notificacoes[f"{traceId}"])
