import asyncio
import random
from functools import partial
from json import loads

import aio_pika

from backend import config, model


async def callback(message: aio_pika.IncomingMessage, channel=None, notificacoes=None):
    async with message.process():
        body = loads(message.body.decode())

        match notificacoes[body["content"]["traceId"]].tipoNotificacao:
            case model.TipoNotificacao.EMAIL:
                await asyncio.sleep(random.uniform(0.5, 1))
            case model.TipoNotificacao.SMS:
                await asyncio.sleep(random.uniform(1, 2))
            case model.TipoNotificacao.PUSH:
                await asyncio.sleep(random.uniform(0.2, 2))
            case _:
                ...

        if random.random() < 0.05:
            notificacoes[body["content"]["traceId"]].statusNotificacao = (
                model.StatusNotificacao.FALHA_ENVIO_FINAL
            )
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.body),
                routing_key="fila.notificacao.dlq.caiomelo",
            )
        else:
            notificacoes[body["content"]["traceId"]].statusNotificacao = (
                model.StatusNotificacao.ENVIADO_SUCESSO
            )


async def main(notificacoes):
    connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
    channel = await connection.channel()
    await channel.declare_queue("fila.notificacao.dlq.caiomelo", durable=True)

    queue = await channel.declare_queue(
        "fila.notificacao.validacao.caiomelo",
        durable=True,
    )

    print(f" [VALIDACAO] Esperando mensagens. {id(notificacoes):x}")
    await queue.consume(partial(callback, channel=channel, notificacoes=notificacoes))
