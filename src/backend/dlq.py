import asyncio
import random
from functools import partial
from json import loads

import aio_pika

from backend import config, model


async def callback(message: aio_pika.IncomingMessage, channel=None, notificacoes=None):
    async with message.process():
        body = loads(message.body.decode())
        print(
            f"FALHA NO PROCESSAMENTO: {body["content"]["traceId"]}: {body["content"]["conteudoMensagem"]}"
        )


async def main(notificacoes):
    connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("fila.notificacao.dlq.caiomelo", durable=True)
    await queue.consume(partial(callback, channel=channel, notificacoes=notificacoes))
    print(" [DLQ] Esperando mensagens.")
    await asyncio.Future()
