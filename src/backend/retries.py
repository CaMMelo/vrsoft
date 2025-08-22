import aio_pika
import asyncio
import random
from functools import partial
from backend import model
from json import loads
from backend import config


async def callback(message: aio_pika.IncomingMessage, channel = None):
    async with message.process():
        await asyncio.sleep(3)
        body = loads(message.body.decode())
        if random.random() < 0.2:
            model.notificacoes[body["content"]["traceId"]].statusNotificacao = model.StatusNotificacao.FALHA_FINAL_PROCESSAMENTO
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.body),
                routing_key="fila.notificacao.dlq.caiomelo",
            )
        else:
            model.notificacoes[body["content"]["traceId"]].statusNotificacao = model.StatusNotificacao.REPROCESSADO_COM_SUCESSO
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.body),
                routing_key="fila.notificacao.validacao.caiomelo",
            )


async def main():
    connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
    channel = await connection.channel()
    await channel.declare_queue("fila.notificacao.dlq.caiomelo", durable=True)
    await channel.declare_queue("fila.notificacao.validacao.caiomelo", durable=True)
    
    queue = await channel.declare_queue("fila.notificacao.retry.caiomelo", durable=True)

    await queue.consume(partial(callback, channel=channel))
    
    print(" [RETRY] Esperando mensagens.")
    await asyncio.Future()
