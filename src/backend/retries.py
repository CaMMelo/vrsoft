import asyncio
import random
from functools import partial
from json import loads

import aio_pika

from backend import config, model


async def callback(message: aio_pika.IncomingMessage, channel=None, notificacoes=None):
    async with message.process():
        await asyncio.sleep(3)
        body = loads(message.body.decode())
        if random.random() < 0.2:
            notificacoes[body["content"]["traceId"]].statusNotificacao = (
                model.StatusNotificacao.FALHA_FINAL_PROCESSAMENTO
            )
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.body),
                routing_key="fila.notificacao.dlq.caiomelo",
            )
        else:
            notificacoes[body["content"]["traceId"]].statusNotificacao = (
                model.StatusNotificacao.REPROCESSADO_COM_SUCESSO
            )
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.body),
                routing_key="fila.notificacao.validacao.caiomelo",
            )


async def main(notificacoes):
    connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
    channel = await connection.channel()
    await channel.declare_queue("fila.notificacao.dlq.caiomelo", durable=True)
    await channel.declare_queue("fila.notificacao.validacao.caiomelo", durable=True)

    queue = await channel.declare_queue("fila.notificacao.retry.caiomelo", durable=True)

    print(f" [RETRY] Esperando mensagens. {id(notificacoes):x}")
    await queue.consume(partial(callback, channel=channel, notificacoes=notificacoes))
