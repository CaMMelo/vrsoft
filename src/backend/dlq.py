import aio_pika
import asyncio
import random
from functools import partial
from backend import model
from json import loads
from backend import config


async def callback(message: aio_pika.IncomingMessage, channel = None):
    async with message.process():
        body = loads(message.body.decode())
        print(f"FALHA NO PROCESSAMENTO: {body["content"]["traceId"]}: {body["content"]["conteudoMensagem"]}")


async def main():
    connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("fila.notificacao.dlq.caiomelo", durable=True)
    await queue.consume(partial(callback, channel=channel))
    print(" [DLQ] Esperando mensagens.")
    await asyncio.Future()
