import asyncio
import random
from functools import partial
from json import loads

import aio_pika

from backend import config, model


async def callback(message: aio_pika.IncomingMessage, channel=None, notificacoes=None):
    async with message.process():
        body = loads(message.body.decode())
        if random.random() < 0.15:
            notificacoes[body["content"]["traceId"]].statusNotificacao = (
                model.StatusNotificacao.FALHA_PROCESSAMENTO_INICIAL
            )
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.body),
                routing_key="fila.notificacao.retry.caiomelo",
            )
        else:
            await asyncio.sleep(random.uniform(1, 1.5))
            notificacoes[body["content"]["traceId"]].statusNotificacao = (
                model.StatusNotificacao.PROCESSADO_INTERMEDIARIO
            )
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.body),
                routing_key="fila.notificacao.validacao.caiomelo",
            )


async def main(notificacoes):
    connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
    channel = await connection.channel()
    await channel.declare_queue("fila.notificacao.retry.caiomelo", durable=True)
    await channel.declare_queue("fila.notificacao.validacao.caiomelo", durable=True)

    queue = await channel.declare_queue(
        "fila.notificacao.entrada.caiomelo", durable=True
    )

    print(f" [ENTRADA] Esperando mensagens. {id(notificacoes):x}")
    await queue.consume(partial(callback, channel=channel, notificacoes=notificacoes))
