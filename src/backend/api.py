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
    app.state.rabbitmq_connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
    app.state.rabbitmq_channel = await app.state.rabbitmq_connection.channel()

    from backend import dlq, entrada, retries, validacao

    app.state.consumer_task = asyncio.create_task(entrada.main())
    app.state.consumer_task = asyncio.create_task(validacao.main())
    app.state.consumer_task = asyncio.create_task(retries.main())
    app.state.consumer_task = asyncio.create_task(dlq.main())


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.rabbitmq_connection.close()


@app.post("/api/notificar", status_code=status.HTTP_202_ACCEPTED)
async def __notificar(payload: model.PayloadNotificacao, request: Request):
    traceId = f"{uuid4()}"
    model.notificacoes[traceId] = model.Notificacao(
        traceId=traceId,
        mensagemId=payload.mensagemId,
        conteudoMensagem=payload.conteudoMensagem,
        tipoNotificacao=model.TipoNotificacao(payload.tipoNotificacao),
        statusNotificacao=model.StatusNotificacao.RECEBIDO,
    )

    channel = request.app.state.rabbitmq_channel
    await channel.declare_queue("fila.notificacao.entrada.caiomelo", durable=True)
    message_body = json.dumps(
        {"content": asdict(model.notificacoes[traceId])}, default=str
    ).encode()
    await channel.default_exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="fila.notificacao.entrada.caiomelo",
    )
    return {
        "mensagemId": payload.mensagemId,
        "traceId": traceId,
    }


@app.get("/api/notificacao/status/{traceId}")
def __status(traceId: UUID):
    if f"{traceId}" not in model.notificacoes:
        raise HTTPException(status_code=404, detail="notificacao nao encontrada.")
    return asdict(model.notificacoes[f"{traceId}"])
